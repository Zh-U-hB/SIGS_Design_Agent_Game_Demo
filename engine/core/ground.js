import * as THREE from 'three';
import { COLORS, MATERIAL_DEFAULTS } from '../utils/color-palette.js';

export function createGround(scene) {
    const groundGeo = new THREE.PlaneGeometry(300, 300);
    const groundMat = new THREE.MeshStandardMaterial({
        color: COLORS.environment.ground,
        ...MATERIAL_DEFAULTS,
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    ground.userData.isGround = true;
    scene.add(ground);

    return ground;
}

export function createRoads(scene) {
    const roadMat = new THREE.MeshStandardMaterial({
        color: COLORS.environment.road,
        ...MATERIAL_DEFAULTS,
        roughness: 0.95,
    });

    const roads = [];

    const mainRoadGeo = new THREE.PlaneGeometry(12, 300);
    const mainRoad = new THREE.Mesh(mainRoadGeo, roadMat);
    mainRoad.rotation.x = -Math.PI / 2;
    mainRoad.position.y = 0.02;
    mainRoad.receiveShadow = true;
    mainRoad.userData.isGround = true;
    scene.add(mainRoad);
    roads.push(mainRoad);

    const crossRoadGeo = new THREE.PlaneGeometry(300, 12);
    const crossRoad = new THREE.Mesh(crossRoadGeo, roadMat);
    crossRoad.rotation.x = -Math.PI / 2;
    crossRoad.position.y = 0.02;
    crossRoad.receiveShadow = true;
    crossRoad.userData.isGround = true;
    scene.add(crossRoad);
    roads.push(crossRoad);

    return roads;
}
