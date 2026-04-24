import * as THREE from 'three';

const WORLD_BOUNDS = { minX: -150, maxX: 150, minZ: -150, maxZ: 150 };

export function worldToScreen(worldPos, camera, container) {
    const vec = new THREE.Vector3(worldPos.x, worldPos.y, worldPos.z);
    vec.project(camera);

    const halfW = container.clientWidth / 2;
    const halfH = container.clientHeight / 2;

    return {
        x: (vec.x * halfW) + halfW,
        y: -(vec.y * halfH) + halfH,
        left: ((vec.x + 1) / 2) * 100,
        top: ((-vec.y + 1) / 2) * 100,
    };
}

export function screenToWorld(screenPercent, camera, container) {
    const ndcX = (screenPercent.left / 100) * 2 - 1;
    const ndcY = -(screenPercent.top / 100) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);

    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
    const intersection = new THREE.Vector3();
    raycaster.ray.intersectPlane(groundPlane, intersection);

    return intersection;
}

export function worldToDbCoords(worldPos) {
    const rangeX = WORLD_BOUNDS.maxX - WORLD_BOUNDS.minX;
    const rangeZ = WORLD_BOUNDS.maxZ - WORLD_BOUNDS.minZ;

    return {
        location_x: ((worldPos.x - WORLD_BOUNDS.minX) / rangeX) * 100,
        location_y: ((worldPos.z - WORLD_BOUNDS.minZ) / rangeZ) * 100,
        location_z: worldPos.y || 0,
    };
}

export function dbCoordsToWorld(dbCoords) {
    const rangeX = WORLD_BOUNDS.maxX - WORLD_BOUNDS.minX;
    const rangeZ = WORLD_BOUNDS.maxZ - WORLD_BOUNDS.minZ;

    return new THREE.Vector3(
        WORLD_BOUNDS.minX + (dbCoords.location_x / 100) * rangeX,
        dbCoords.location_z || 0,
        WORLD_BOUNDS.minZ + (dbCoords.location_y / 100) * rangeZ,
    );
}
