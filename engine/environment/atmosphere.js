import * as THREE from 'three';
import { COLORS } from '../utils/color-palette.js';

export function setupAtmosphere(scene) {
    scene.background = new THREE.Color(COLORS.environment.sky);
    scene.fog = new THREE.Fog(COLORS.environment.sky, 80, 200);
}
