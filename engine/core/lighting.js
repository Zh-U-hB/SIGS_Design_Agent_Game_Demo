import * as THREE from 'three';
import { COLORS } from '../utils/color-palette.js';

export function setupLighting(scene) {
    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambient);

    const hemisphere = new THREE.HemisphereLight(0x87ceeb, 0x7cba3d, 0.3);
    scene.add(hemisphere);

    const sun = new THREE.DirectionalLight(0xffffff, 0.8);
    sun.position.set(50, 100, 50);
    sun.castShadow = true;

    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 300;
    sun.shadow.camera.left = -100;
    sun.shadow.camera.right = 100;
    sun.shadow.camera.top = 100;
    sun.shadow.camera.bottom = -100;
    sun.shadow.bias = -0.001;

    scene.add(sun);

    return { ambient, hemisphere, sun };
}
