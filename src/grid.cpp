#include "grid.hpp"
#include <cmath>
#include <algorithm>
#include <omp.h>

Grille CreateGrid(int resolution_x, int resolution_y, int resolution_z, float scale) {
    Grille grid(resolution_x, resolution_y, resolution_z);

    int nx = resolution_x;
    int ny = resolution_y;
    int nz = resolution_z;
    grid.vertices.resize(nx * ny * nz);

    // Positions sans utilisé push back -> parallèle
    #pragma omp parallel for collapse(3) schedule(static)
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                int id = idx3(i, j, k, ny, nz);
                float x = i * scale;
                float y = j * scale + 5;
                float z = k * scale;
                grid.vertices[id] = { x, y, z };
            }
        }
    }

    return grid;
}

void UpdateGrid(float dt, Grille& grid, bool pressure, bool speed) {
    const float g = -9.81f;
    const float nu = 1.3f;                // viscosité
    const float radius = 1.0f;
    const float h = 1.2f;                 // rayon d'action
    const float stiffness = 0.6f;         // facteur de pression sur les autres particules
    const float wallStiffness = 2.0f;     // facteur de pression du mur
    const float wallDamping = 0.8f;       // amorti du mur
    const float epsilon = 1e-4f;

    const int nx = grid.nx;
    const int ny = grid.ny;
    const int nz = grid.nz;
    const int N = nx * ny * nz;

    const float minX = 0.0f, maxX = 20.0f;
    const float minY = 0.0f, maxY = 60.0f;
    const float minZ = 0.0f, maxZ = 20.0f;

    const float restDensity = (maxX - minX) * (maxY - minY) * (maxZ - minZ) / float(N);

    // ---- PHASE 0: Accélerations ----
    #pragma omp parallel for collapse(3) schedule(static)
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                grid.ax[i][j][k] = 0.0f;
                grid.ay[i][j][k] = g; 
                grid.az[i][j][k] = 0.0f;
            }
        }
    }

    // ---- PHASE 1: Calcul de densité ----
    #pragma omp parallel for collapse(3) schedule(dynamic)
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                int id = idx3(i, j, k, ny, nz);
                const Vertex& v = grid.vertices[id];

                float density = 0.0f;

                for (int ii = 0; ii < nx; ++ii) {
                    for (int jj = 0; jj < ny; ++jj) {
                        for (int kk = 0; kk < nz; ++kk) {
                            if (ii == i && jj == j && kk == k) continue;
                            int nid = idx3(ii, jj, kk, ny, nz);
                            const Vertex& n = grid.vertices[nid];

                            float dx = v.x - n.x;
                            float dy = v.y - n.y;
                            float dz = v.z - n.z;
                            float r2 = dx*dx + dy*dy + dz*dz;
                            if (r2 > 0.0f && r2 < h*h) {
                                float r = std::sqrt(r2);
                                float q = 1.0f - r / h;
                                density += q * q;
                            }
                        }
                    }
                }

                grid.div[i][j][k] = density;
            }
        }
    }

    // ---- PHASE 2: Force (Pression + Viscosité + Murs) ----
    #pragma omp parallel for collapse(3) schedule(dynamic)
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                int id = idx3(i, j, k, ny, nz);
                const Vertex& A = grid.vertices[id];

                float rhoA = grid.div[i][j][k];
                float PA = stiffness * (rhoA - restDensity);

                float ax_local = grid.ax[i][j][k]; 
                float ay_local = grid.ay[i][j][k];
                float az_local = grid.az[i][j][k];

                // neighbor interactions
                for (int ii = 0; ii < nx; ++ii) {
                    for (int jj = 0; jj < ny; ++jj) {
                        for (int kk = 0; kk < nz; ++kk) {
                            if (ii == i && jj == j && kk == k) continue;
                            int nid = idx3(ii, jj, kk, ny, nz);
                            const Vertex& B = grid.vertices[nid];

                            float dx = B.x - A.x;
                            float dy = B.y - A.y;
                            float dz = B.z - A.z;
                            float r = std::sqrt(dx*dx + dy*dy + dz*dz);
                            if (r <= 0.0f || r > h) continue;

                            float q = 1.0f - r / h;
                            float rhoB = grid.div[ii][jj][kk];
                            float PB = stiffness * (rhoB - restDensity);

                            float nx_ = dx / r;
                            float ny_ = dy / r;
                            float nz_ = dz / r;

                            // Contribution à la pression
                            float fPress = -0.5f * (PA + PB) * q;

                            ax_local += fPress * nx_;
                            ay_local += fPress * ny_;
                            az_local += fPress * nz_;

                            // Viscosité
                            float vxDiff = grid.vx[ii][jj][kk] - grid.vx[i][j][k];
                            float vyDiff = grid.vy[ii][jj][kk] - grid.vy[i][j][k];
                            float vzDiff = grid.vz[ii][jj][kk] - grid.vz[i][j][k];

                            ax_local += nu * vxDiff * q;
                            ay_local += nu * vyDiff * q;
                            az_local += nu * vzDiff * q;
                        }
                    }
                }

                // Murs
                if (A.x - radius < minX) 
                    ax_local += wallStiffness * (minX - (A.x - radius));
                if (A.x + radius > maxX) 
                    ax_local -= wallStiffness * ((A.x + radius) - maxX);
                if (A.y - radius < minY) 
                    ay_local += wallStiffness * (minY - (A.y - radius));
                if (A.y + radius > maxY) 
                    ay_local -= wallStiffness * ((A.y + radius) - maxY);
                if (A.z - radius < minZ) 
                    az_local += wallStiffness * (minZ - (A.z - radius));
                if (A.z + radius > maxZ) 
                    az_local -= wallStiffness * ((A.z + radius) - maxZ);

                // Stockage
                grid.ax[i][j][k] = ax_local;
                grid.ay[i][j][k] = ay_local;
                grid.az[i][j][k] = az_local;

                if(pressure){
                    // Normalisation de la pression entre 0 et 1
                    float Pnorm = std::clamp((PA - (-restDensity)) / (restDensity * 2.0f), 0.0f, 1.0f);

                    // Dégradé du bleu (faible pression) au rouge (forte pression)
                    float r = Pnorm;
                    float g = 0.2f * (1.0f - Pnorm);
                    float b = 1.0f - Pnorm;

                    // Stocke la couleur dans le vertex
                    grid.vertices[id].r = r;
                    grid.vertices[id].g = g;
                    grid.vertices[id].b = b;
                } else if(!speed){
                    grid.vertices[id].r = 0;
                    grid.vertices[id].g = 0;
                    grid.vertices[id].b = 1;
                }
            }
        }
    }

    // ---- PHASE 3: Intégration----
    #pragma omp parallel for collapse(3) schedule(static)
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                int id = idx3(i, j, k, ny, nz);
                Vertex& v = grid.vertices[id];

                float& vx = grid.vx[i][j][k];
                float& vy = grid.vy[i][j][k];
                float& vz = grid.vz[i][j][k];

                float ax_ = grid.ax[i][j][k];
                float ay_ = grid.ay[i][j][k];
                float az_ = grid.az[i][j][k];

                vx += ax_ * dt;
                vy += ay_ * dt;
                vz += az_ * dt;

                v.x += vx * dt;
                v.y += vy * dt;
                v.z += vz * dt;

                if (v.x < minX + epsilon) {
                    v.x = minX + epsilon;
                    vx = -vx * wallDamping;
                } else if (v.x > maxX - epsilon) {
                    v.x = maxX - epsilon;
                    vx = -vx * wallDamping;
                }

                if (v.y < minY + epsilon) {
                    v.y = minY + epsilon;
                    vy = -vy * wallDamping;
                } else if (v.y > maxY - epsilon) {
                    v.y = maxY - epsilon;
                    vy = -vy * wallDamping;
                }

                if (v.z < minZ + epsilon) {
                    v.z = minZ + epsilon;
                    vz = -vz * wallDamping;
                } else if (v.z > maxZ - epsilon) {
                    v.z = maxZ - epsilon;
                    vz = -vz * wallDamping;
                }

                if (speed) {
                    float norm_v = sqrt(vx*vx + vy*vy + vz*vz);
                    float v_norm = fmin(norm_v / 15, 1.0f); // clamp entre 0 et 1

                    float r = v_norm;
                    float g = 0.2f * (1.0f - v_norm);
                    float b = 1.0f - v_norm;

                    grid.vertices[id].r = r;
                    grid.vertices[id].g = g;
                    grid.vertices[id].b = b;
                }
            }
        }
    }
}

Vertex ComputeAverageVelocity(const Grille& grid) {
    double total_vx = 0.0;
    double total_vy = 0.0;
    double total_vz = 0.0;
    int nx = grid.nx, ny = grid.ny, nz = grid.nz;
    int count = nx * ny * nz;

    #pragma omp parallel for reduction(+:total_vx,total_vy,total_vz) collapse(3)
    for (int i = 0; i < nx; ++i) {
        for (int j = 0; j < ny; ++j) {
            for (int k = 0; k < nz; ++k) {
                total_vx += grid.vx[i][j][k];
                total_vy += grid.vy[i][j][k];
                total_vz += grid.vz[i][j][k];
            }
        }
    }

    return { float(total_vx / count), float(total_vy / count), float(total_vz / count) };
}