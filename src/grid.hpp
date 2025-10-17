#pragma once
#include <iostream>
#include <vector>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <omp.h>

struct Vertex {
    float x, y, z;
    float r, g, b; // ← couleur
};


struct Grille {
    std::vector<Vertex> vertices;

    int nx, ny, nz;     
    std::vector<std::vector<std::vector<float>>> vx;       
    std::vector<std::vector<std::vector<float>>> vy; 
    std::vector<std::vector<std::vector<float>>> vz;      
    std::vector<std::vector<std::vector<float>>> ax;       
    std::vector<std::vector<std::vector<float>>> ay;   
    std::vector<std::vector<std::vector<float>>> az;  
    std::vector<std::vector<std::vector<float>>> pressure; 
    std::vector<std::vector<std::vector<float>>> div;      

    // Constructeur
    Grille(int nx_, int ny_, int nz_) : nx(nx_), ny(ny_), nz(nz_) {
        vx.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
        vy.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
        vz.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
        ax.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
        ay.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
        az.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
        pressure.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
        div.resize(nx, std::vector<std::vector<float>>(ny, std::vector<float>(nz, 0.0f)));
    }
};

inline int idx3(int i, int j, int k, int ny, int nz) {
    return i * (ny * nz) + j * nz + k;
}

Grille CreateGrid(int resolution_x, int resolution_y, int resolution_z, float scale);
void UpdateGrid(float time, Grille& grid, bool pressure, bool speed);
Vertex ComputeAverageVelocity(const Grille& grid);
