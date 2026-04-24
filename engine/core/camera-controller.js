import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { ROAM_WAYPOINTS } from '../buildings/campus-layout.js';

export class CameraController {
    constructor(camera, domElement, registerFrame) {
        this._camera = camera;
        this._domElement = domElement;
        this._registerFrame = registerFrame;

        this._mode = 'orbit';
        this._orbitControls = null;
        this._roamCurve = null;
        this._roamProgress = 0;
        this._roamSpeed = 0.0003;

        this._keys = {};
        this._freeSpeed = 0.5;
        this._freeRotSpeed = 0.003;
        this._freeDragging = false;
        this._freeLastMouse = { x: 0, y: 0 };

        this._defaultPosition = new THREE.Vector3(50, 40, 50);
        this._defaultTarget = new THREE.Vector3(0, 0, 0);

        this._initOrbit();
        this._initRoam();
        this._initFree();

        // OrbitControls.update() 需要在每帧调用（启用 damping 时）
        this._registerFrame(() => {
            if (this._orbitControls && this._orbitControls.enabled) {
                this._orbitControls.update();
            }
        });
    }

    setMode(mode) {
        this._disableAll();
        this._mode = mode;

        switch (mode) {
            case 'orbit':
                this._orbitControls.enabled = true;
                break;
            case 'roam':
                this._registerFrame(this._roamTick.bind(this));
                break;
            case 'free':
                this._bindFreeEvents();
                this._registerFrame(this._freeTick.bind(this));
                break;
        }
    }

    flyTo(position) {
        const target = new THREE.Vector3(position.x, position.y, position.z);
        const start = this._camera.position.clone();
        const startTime = performance.now();
        const duration = 1500;

        const tick = () => {
            const elapsed = performance.now() - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3);

            this._camera.position.lerpVectors(start, target, eased);
            this._camera.lookAt(0, 0, 0);

            if (t < 1) {
                requestAnimationFrame(tick);
            }
        };
        tick();
    }

    reset() {
        this._camera.position.copy(this._defaultPosition);
        this._camera.lookAt(this._defaultTarget);
        if (this._orbitControls) {
            this._orbitControls.target.copy(this._defaultTarget);
            this._orbitControls.update();
        }
    }

    destroy() {
        this._disableAll();
        if (this._orbitControls) {
            this._orbitControls.dispose();
        }
    }

    _initOrbit() {
        this._orbitControls = new OrbitControls(this._camera, this._domElement);
        this._orbitControls.enableDamping = true;
        this._orbitControls.dampingFactor = 0.05;
        this._orbitControls.maxPolarAngle = Math.PI / 2.1;
        this._orbitControls.minDistance = 15;
        this._orbitControls.maxDistance = 120;
        this._orbitControls.target.set(0, 0, 0);
    }

    _initRoam() {
        const points = ROAM_WAYPOINTS.map(p => new THREE.Vector3(p.x, p.y, p.z));
        points.push(points[0].clone());
        this._roamCurve = new THREE.CatmullRomCurve3(points, true);
    }

    _roamTick() {
        if (this._mode !== 'roam') return;
        this._roamProgress += this._roamSpeed;
        if (this._roamProgress > 1) this._roamProgress -= 1;

        const pos = this._roamCurve.getPointAt(this._roamProgress);
        const lookAt = this._roamCurve.getPointAt((this._roamProgress + 0.01) % 1);
        this._camera.position.copy(pos);
        this._camera.lookAt(lookAt);
    }

    _initFree() {
        this._onKeyDown = (e) => { this._keys[e.code] = true; };
        this._onKeyUp = (e) => { this._keys[e.code] = false; };
        this._onMouseDown = (e) => {
            if (e.button === 0) {
                this._freeDragging = true;
                this._freeLastMouse = { x: e.clientX, y: e.clientY };
            }
        };
        this._onMouseUp = () => { this._freeDragging = false; };
        this._onMouseMove = (e) => {
            if (!this._freeDragging) return;
            const dx = e.clientX - this._freeLastMouse.x;
            const dy = e.clientY - this._freeLastMouse.y;
            this._camera.rotation.y -= dx * this._freeRotSpeed;
            this._camera.rotation.x -= dy * this._freeRotSpeed;
            this._camera.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, this._camera.rotation.x));
            this._freeLastMouse = { x: e.clientX, y: e.clientY };
        };
    }

    _bindFreeEvents() {
        document.addEventListener('keydown', this._onKeyDown);
        document.addEventListener('keyup', this._onKeyUp);
        this._domElement.addEventListener('mousedown', this._onMouseDown);
        document.addEventListener('mouseup', this._onMouseUp);
        document.addEventListener('mousemove', this._onMouseMove);
    }

    _unbindFreeEvents() {
        document.removeEventListener('keydown', this._onKeyDown);
        document.removeEventListener('keyup', this._onKeyUp);
        this._domElement.removeEventListener('mousedown', this._onMouseDown);
        document.removeEventListener('mouseup', this._onMouseUp);
        document.removeEventListener('mousemove', this._onMouseMove);
    }

    _freeTick() {
        if (this._mode !== 'free') return;

        const forward = new THREE.Vector3();
        this._camera.getWorldDirection(forward);
        forward.y = 0;
        forward.normalize();

        const right = new THREE.Vector3();
        right.crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();

        const move = new THREE.Vector3();
        if (this._keys['KeyW']) move.add(forward);
        if (this._keys['KeyS']) move.sub(forward);
        if (this._keys['KeyA']) move.sub(right);
        if (this._keys['KeyD']) move.add(right);

        if (move.length() > 0) {
            move.normalize().multiplyScalar(this._freeSpeed);
            this._camera.position.add(move);
            this._camera.position.y = 2;
        }
    }

    _disableAll() {
        if (this._orbitControls) this._orbitControls.enabled = false;
        this._unbindFreeEvents();
        this._keys = {};
        this._freeDragging = false;
    }
}
