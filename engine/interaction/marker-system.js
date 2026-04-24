import * as THREE from 'three';
import { COLORS } from '../utils/color-palette.js';
import { dbCoordsToWorld } from '../utils/coordinate.js';

export class MarkerSystem {
    constructor(scene) {
        this._scene = scene;
        this._markers = [];
        this._designMarkers = [];
    }

    addLocationMarkers(markers) {
        this.clearLocationMarkers();

        for (const m of markers) {
            const marker = this._createLocationMarker(m);
            this._scene.add(marker);
            this._markers.push(marker);
        }
    }

    addDesignMarkers(designs, scene, events) {
        this.clearDesignMarkers();

        for (const d of designs) {
            const pos = d.position
                ? new THREE.Vector3(d.position.x, 0, d.position.y || d.position.z || 0)
                : dbCoordsToWorld({
                    location_x: d.percentX ?? d.location_x,
                    location_y: d.percentY ?? d.location_y,
                    location_z: 0,
                });

            const size = Math.max(1, Math.min(3, 1 + (d.likesCount || 0) * 0.5));
            const marker = this._createDesignDot(pos, size, d.id);
            marker.userData.designId = d.id;

            marker.addEventListener = () => {};
            marker.removeEventListener = () => {};

            scene.add(marker);
            this._designMarkers.push(marker);
        }

        this._setupDesignInteraction(scene, events);
    }

    clearAll() {
        this.clearLocationMarkers();
        this.clearDesignMarkers();
    }

    highlight(id) {
        for (const m of [...this._markers, ...this._designMarkers]) {
            if (m.userData.markerId === id) {
                m.scale.set(1.5, 1.5, 1.5);
            } else {
                m.scale.set(1, 1, 1);
            }
        }
    }

    clearLocationMarkers() {
        for (const m of this._markers) {
            this._scene.remove(m);
        }
        this._markers = [];
    }

    clearDesignMarkers() {
        for (const m of this._designMarkers) {
            this._scene.remove(m);
        }
        this._designMarkers = [];
    }

    destroy() {
        if (this._designInteractionCleanup) {
            this._designInteractionCleanup();
        }
        this.clearAll();
    }

    _createLocationMarker(data) {
        const group = new THREE.Group();
        group.userData.markerId = data.id;

        const sphereGeo = new THREE.SphereGeometry(1.5, 12, 8);
        const sphereMat = new THREE.MeshStandardMaterial({
            color: COLORS.markers.location,
            emissive: COLORS.markers.location,
            emissiveIntensity: 0.4,
            transparent: true,
            opacity: 0.8,
        });
        const sphere = new THREE.Mesh(sphereGeo, sphereMat);
        sphere.position.y = data.height ? data.height + 3 : 3;
        group.add(sphere);

        const ringGeo = new THREE.RingGeometry(1.8, 2.2, 24);
        const ringMat = new THREE.MeshBasicMaterial({
            color: COLORS.markers.location,
            transparent: true,
            opacity: 0.5,
            side: THREE.DoubleSide,
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = -Math.PI / 2;
        ring.position.y = 0.1;
        group.add(ring);

        if (data.position) {
            group.position.set(data.position.x, 0, data.position.z || 0);
        }

        return group;
    }

    _createDesignDot(position, size, id) {
        const geo = new THREE.SphereGeometry(size, 8, 6);
        const mat = new THREE.MeshStandardMaterial({
            color: COLORS.markers.design,
            emissive: COLORS.markers.design,
            emissiveIntensity: 0.3,
            transparent: true,
            opacity: 0.85,
        });
        const dot = new THREE.Mesh(geo, mat);
        dot.position.copy(position);
        dot.position.y = 1 + size;
        dot.userData.markerId = id;
        dot.userData.isDesignMarker = true;
        return dot;
    }

    _setupDesignInteraction(scene, events) {
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let hoveredMarker = null;

        const onPointerMove = (event) => {
            const rect = scene.renderer?.domElement?.getBoundingClientRect() || event.target.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, scene.camera);

            const intersects = raycaster.intersectObjects(this._designMarkers);

            if (intersects.length > 0) {
                const marker = intersects[0].object;
                if (hoveredMarker !== marker) {
                    if (hoveredMarker) {
                        hoveredMarker.scale.set(1, 1, 1);
                        hoveredMarker.material.emissiveIntensity = 0.3;
                    }
                    hoveredMarker = marker;
                    hoveredMarker.scale.set(1.3, 1.3, 1.3);
                    hoveredMarker.material.emissiveIntensity = 0.6;
                    event.target.style.cursor = 'pointer';
                    events.emit('marker-hovered', { id: marker.userData.designId });
                }
            } else {
                if (hoveredMarker) {
                    hoveredMarker.scale.set(1, 1, 1);
                    hoveredMarker.material.emissiveIntensity = 0.3;
                    hoveredMarker = null;
                    event.target.style.cursor = 'grab';
                }
            }
        };

        const onPointerClick = (event) => {
            if (hoveredMarker) {
                events.emit('marker-clicked', { id: hoveredMarker.userData.designId });
            }
        };

        const container = scene.renderer?.domElement?.parentElement || window;
        container.addEventListener('pointermove', onPointerMove);
        container.addEventListener('click', onPointerClick);

        this._designInteractionCleanup = () => {
            container.removeEventListener('pointermove', onPointerMove);
            container.removeEventListener('click', onPointerClick);
        };
    }
}
