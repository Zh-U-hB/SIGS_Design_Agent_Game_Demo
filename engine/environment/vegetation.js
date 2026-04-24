import * as THREE from 'three';
import { COLORS, MATERIAL_DEFAULTS } from '../utils/color-palette.js';

export function createTree(scale = 1) {
    const group = new THREE.Group();

    const trunkGeo = new THREE.CylinderGeometry(0.3 * scale, 0.5 * scale, 3 * scale, 6);
    const trunkMat = new THREE.MeshStandardMaterial({
        color: COLORS.vegetation.trunk,
        ...MATERIAL_DEFAULTS,
    });
    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.y = 1.5 * scale;
    trunk.castShadow = true;
    group.add(trunk);

    const foliageGeo = new THREE.DodecahedronGeometry(2.5 * scale);
    const foliageMat = new THREE.MeshStandardMaterial({
        color: COLORS.vegetation.tree,
        ...MATERIAL_DEFAULTS,
    });
    const foliage = new THREE.Mesh(foliageGeo, foliageMat);
    foliage.position.y = 4.5 * scale;
    foliage.castShadow = true;
    group.add(foliage);

    return group;
}

export function createForest(scene) {
    const count = 60;
    const trunkGeo = new THREE.CylinderGeometry(0.3, 0.5, 3, 6);
    const trunkMat = new THREE.MeshStandardMaterial({
        color: COLORS.vegetation.trunk,
        ...MATERIAL_DEFAULTS,
    });
    const instancedTrunks = new THREE.InstancedMesh(trunkGeo, trunkMat, count);
    instancedTrunks.castShadow = true;

    const foliageGeo = new THREE.DodecahedronGeometry(2.5);
    const foliageMat = new THREE.MeshStandardMaterial({
        color: COLORS.vegetation.tree,
        ...MATERIAL_DEFAULTS,
    });
    const instancedFoliage = new THREE.InstancedMesh(foliageGeo, foliageMat, count);
    instancedFoliage.castShadow = true;

    const matrix = new THREE.Matrix4();
    const scaleMatrix = new THREE.Matrix4();
    let idx = 0;

    for (let i = 0; i < count; i++) {
        let x, z;
        do {
            x = (Math.random() - 0.5) * 260;
            z = (Math.random() - 0.5) * 260;
        } while (
            (Math.abs(x) < 10 || Math.abs(z) < 10) ||
            isInsideBuilding(x, z)
        );

        const s = 0.7 + Math.random() * 0.6;

        matrix.makeTranslation(x, 1.5 * s, z);
        scaleMatrix.makeScale(s, s, s);
        matrix.multiply(scaleMatrix);
        instancedTrunks.setMatrixAt(i, matrix);

        matrix.makeTranslation(x, 4.5 * s, z);
        scaleMatrix.makeScale(s, s, s);
        matrix.multiply(scaleMatrix);
        instancedFoliage.setMatrixAt(i, matrix);
    }

    instancedTrunks.instanceMatrix.needsUpdate = true;
    instancedFoliage.instanceMatrix.needsUpdate = true;

    scene.add(instancedTrunks);
    scene.add(instancedFoliage);
}

function isInsideBuilding(x, z) {
    const margin = 8;
    const buildingPositions = [
        { x: -60, z: 50, hw: 15, hd: 12 },
        { x: -50, z: -20, hw: 12, hd: 10 },
        { x: -10, z: -40, hw: 10, hd: 9 },
        { x: 30, z: 50, hw: 14, hd: 11 },
        { x: 70, z: -10, hw: 10, hd: 7 },
        { x: 50, z: -60, hw: 17, hd: 12 },
        { x: 80, z: 40, hw: 15, hd: 10 },
        { x: -80, z: -60, hw: 11, hd: 9 },
    ];

    return buildingPositions.some(b =>
        Math.abs(x - b.x) < b.hw + margin && Math.abs(z - b.z) < b.hd + margin,
    );
}
