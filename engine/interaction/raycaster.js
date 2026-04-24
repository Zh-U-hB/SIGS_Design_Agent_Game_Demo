import * as THREE from 'three';
import { worldToScreen, worldToDbCoords } from '../utils/coordinate.js';
import { EventBus } from '../utils/event-bus.js';

export class InteractionManager {
    constructor(scene, camera, domElement, container, buildings) {
        this._scene = scene;
        this._camera = camera;
        this._domElement = domElement;
        this._container = container;
        this._buildings = buildings;
        this._events = new EventBus();

        this._raycaster = new THREE.Raycaster();
        this._pointer = new THREE.Vector2();
        this._hoveredObject = null;

        this._onPointerMove = this._handlePointerMove.bind(this);
        this._onClick = this._handleClick.bind(this);

        this._domElement.addEventListener('pointermove', this._onPointerMove);
        this._domElement.addEventListener('click', this._onClick);
    }

    on(event, callback) {
        this._events.on(event, callback);
    }

    destroy() {
        this._domElement.removeEventListener('pointermove', this._onPointerMove);
        this._domElement.removeEventListener('click', this._onClick);
        this._events.removeAll();
    }

    _getBuildingMeshes() {
        const meshes = [];
        for (const building of this._buildings) {
            building.traverse((child) => {
                if (child.isMesh) {
                    meshes.push(child);
                }
            });
        }
        return meshes;
    }

    _getIntersected(event) {
        const rect = this._domElement.getBoundingClientRect();
        this._pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this._pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this._raycaster.setFromCamera(this._pointer, this._camera);

        const meshes = this._getBuildingMeshes();
        const intersects = this._raycaster.intersectObjects(meshes, false);

        if (intersects.length > 0) {
            const hit = intersects[0];
            const buildingGroup = this._findBuildingGroup(hit.object);
            if (buildingGroup) {
                const screenPos = worldToScreen(
                    hit.point, this._camera, this._container,
                );
                const dbCoords = worldToDbCoords(hit.point);
                return {
                    object: buildingGroup,
                    worldPosition: hit.point,
                    screenPosition: screenPos,
                    screenPercent: { left: dbCoords.location_x, top: dbCoords.location_y },
                };
            }
        }
        return null;
    }

    _findBuildingGroup(mesh) {
        let current = mesh;
        while (current) {
            if (current.userData && current.userData.isBuilding) {
                return current;
            }
            current = current.parent;
        }
        return null;
    }

    _handlePointerMove(event) {
        const result = this._getIntersected(event);

        if (result) {
            if (this._hoveredObject !== result.object) {
                if (this._hoveredObject) {
                    this._setEmissive(this._hoveredObject, 0x000000);
                    this._events.emit('hover-end', {});
                }
                this._hoveredObject = result.object;
                this._setEmissive(this._hoveredObject, 0x222222);
                this._events.emit('hover', {
                    object: result.object,
                    screenPosition: result.screenPosition,
                });
            }
            this._domElement.style.cursor = 'pointer';
        } else {
            if (this._hoveredObject) {
                this._setEmissive(this._hoveredObject, 0x000000);
                this._hoveredObject = null;
                this._events.emit('hover-end', {});
            }
            this._domElement.style.cursor = 'default';
        }
    }

    _handleClick(event) {
        const result = this._getIntersected(event);
        if (result) {
            this._events.emit('click', {
                object: result.object,
                worldPosition: result.worldPosition,
                screenPosition: result.screenPosition,
                screenPercent: result.screenPercent,
            });
        }
    }

    _setEmissive(buildingGroup, color) {
        buildingGroup.traverse((child) => {
            if (child.isMesh && child.material && child.material.emissive) {
                child.material.emissive.setHex(color);
                child.material.emissiveIntensity = color === 0x000000 ? 0 : 0.15;
            }
        });
    }
}
