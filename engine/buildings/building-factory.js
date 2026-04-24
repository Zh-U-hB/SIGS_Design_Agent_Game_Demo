import * as THREE from 'three';
import { MATERIAL_DEFAULTS } from '../utils/color-palette.js';

export function createBuilding(options) {
    const {
        name = '',
        width = 10,
        depth = 10,
        height = 15,
        color = 0x999999,
        position = { x: 0, y: 0, z: 0 },
        roofType = 'flat',
        windows = true,
        windowRows = 3,
        windowCols = 4,
    } = options;

    const group = new THREE.Group();
    group.userData.name = name;
    group.userData.isBuilding = true;

    const bodyGeo = new THREE.BoxGeometry(width, height, depth);
    const bodyMat = new THREE.MeshStandardMaterial({
        color,
        ...MATERIAL_DEFAULTS,
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = height / 2;
    body.castShadow = true;
    body.receiveShadow = true;
    body.userData.isBuildingPart = true;
    body.userData.parentBuilding = group;
    group.add(body);

    if (roofType !== 'none') {
        const roof = createRoof(roofType, width, depth, height);
        if (roof) {
            roof.castShadow = true;
            group.add(roof);
        }
    }

    if (windows) {
        const windowMeshes = createWindows(width, depth, height, windowRows, windowCols);
        for (const w of windowMeshes) {
            group.add(w);
        }
    }

    group.position.set(position.x, position.y, position.z);

    return group;
}

function createRoof(type, width, depth, height) {
    let geo;
    let mat = new THREE.MeshStandardMaterial({
        color: 0x8b4513,
        ...MATERIAL_DEFAULTS,
    });

    switch (type) {
        case 'pointed':
            geo = new THREE.ConeGeometry(
                Math.max(width, depth) * 0.7,
                height * 0.3,
                4,
            );
            break;
        case 'dome':
            geo = new THREE.SphereGeometry(
                Math.max(width, depth) * 0.5,
                8, 6,
                0, Math.PI * 2,
                0, Math.PI * 0.5,
            );
            break;
        case 'flat':
        default:
            geo = new THREE.BoxGeometry(width + 1, 1, depth + 1);
            mat = new THREE.MeshStandardMaterial({
                color: 0x666666,
                ...MATERIAL_DEFAULTS,
            });
            break;
    }

    const roof = new THREE.Mesh(geo, mat);
    roof.position.y = height + (type === 'flat' ? 0.5 : 0);
    roof.userData.isBuildingPart = true;
    return roof;
}

function createWindows(width, depth, height, rows, cols) {
    const meshes = [];
    const winGeo = new THREE.PlaneGeometry(1, 1.5);
    const winMat = new THREE.MeshStandardMaterial({
        color: 0x87ceeb,
        emissive: 0x87ceeb,
        emissiveIntensity: 0.15,
    });

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const front = new THREE.Mesh(winGeo, winMat);
            front.position.set(
                (col - (cols - 1) / 2) * (width / cols),
                (row + 1) * (height / (rows + 1)),
                depth / 2 + 0.01,
            );
            meshes.push(front);

            const back = new THREE.Mesh(winGeo, winMat);
            back.position.set(
                (col - (cols - 1) / 2) * (width / cols),
                (row + 1) * (height / (rows + 1)),
                -depth / 2 - 0.01,
            );
            back.rotation.y = Math.PI;
            meshes.push(back);
        }
    }

    return meshes;
}
