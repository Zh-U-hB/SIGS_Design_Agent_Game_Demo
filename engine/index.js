import { createScene } from './core/scene.js';
import { setupLighting } from './core/lighting.js';
import { createGround, createRoads } from './core/ground.js';
import { createBuilding } from './buildings/building-factory.js';
import { CAMPUS_BUILDINGS, CAMPUS_ROADS } from './buildings/campus-layout.js';
import { createForest } from './environment/vegetation.js';
import { setupAtmosphere } from './environment/atmosphere.js';
import { CameraController } from './core/camera-controller.js';
import { InteractionManager } from './interaction/raycaster.js';
import { MarkerSystem } from './interaction/marker-system.js';
import { TooltipManager } from './interaction/tooltip.js';
import { captureScreenshot } from './capture/screenshot.js';
import { EventBus } from './utils/event-bus.js';

export class CampusEngine {
    constructor(config) {
        this._config = {
            container: config.container,
            mode: config.mode || 'explore',
            cameraMode: config.cameraMode || 'orbit',
            showBuildings: config.showBuildings !== false,
            showMarkers: config.showMarkers !== false,
            showVegetation: config.showVegetation !== false,
            language: config.language || 'zh',
        };

        this._events = new EventBus();
        this._sceneApi = null;
        this._cameraController = null;
        this._interactionManager = null;
        this._markerSystem = null;
        this._tooltipManager = null;
        this._buildings = [];
    }

    on(event, callback) {
        this._events.on(event, callback);
        return this;
    }

    off(event, callback) {
        this._events.off(event, callback);
        return this;
    }

    start() {
        this._initScene();
        this._initEnvironment();
        this._initCamera();
        this._initInteraction();
        this._sceneApi.start();
        this._events.emit('ready', {});
    }

    stop() {
        if (this._sceneApi) this._sceneApi.stop();
    }

    destroy() {
        if (this._interactionManager) this._interactionManager.destroy();
        if (this._tooltipManager) this._tooltipManager.destroy();
        if (this._markerSystem) this._markerSystem.destroy();
        if (this._cameraController) this._cameraController.destroy();
        if (this._sceneApi) this._sceneApi.destroy();
        this._events.removeAll();
    }

    setCameraMode(mode) {
        if (this._cameraController) {
            this._cameraController.setMode(mode);
            this._events.emit('camera-mode-changed', { mode });
        }
    }

    flyTo(position) {
        if (this._cameraController) {
            this._cameraController.flyTo(position);
        }
    }

    resetCamera() {
        if (this._cameraController) {
            this._cameraController.reset();
        }
    }

    addLocationMarkers(markers) {
        if (this._markerSystem) {
            this._markerSystem.addLocationMarkers(markers);
        }
    }

    addDesignMarkers(designs) {
        if (this._markerSystem) {
            this._markerSystem.addDesignMarkers(designs, this._sceneApi.scene, this._events);
        }
    }

    clearMarkers() {
        if (this._markerSystem) {
            this._markerSystem.clearAll();
        }
    }

    highlightMarker(id) {
        if (this._markerSystem) {
            this._markerSystem.highlight(id);
        }
    }

    setLanguage(lang) {
        this._config.language = lang;
        if (this._tooltipManager) {
            this._tooltipManager.setLanguage(lang);
        }
    }

    captureScreenshot() {
        if (!this._sceneApi) return Promise.resolve('');
        return captureScreenshot(this._sceneApi.renderer, this._sceneApi.scene, this._sceneApi.camera);
    }

    resize() {
        if (this._sceneApi) {
            const w = this._config.container.clientWidth;
            const h = this._config.container.clientHeight;
            this._sceneApi.camera.aspect = w / h;
            this._sceneApi.camera.updateProjectionMatrix();
            this._sceneApi.renderer.setSize(w, h);
        }
    }

    _initScene() {
        this._sceneApi = createScene(this._config.container);
        setupLighting(this._sceneApi.scene);
    }

    _initEnvironment() {
        const { scene } = this._sceneApi;

        createGround(scene);
        createRoads(scene);
        setupAtmosphere(scene);

        if (this._config.showBuildings) {
            this._buildings = CAMPUS_BUILDINGS.map(data => {
                const building = createBuilding(data);
                building.userData.buildingId = data.id;
                building.userData.emotionLabel = data.emotionLabel;
                building.userData.mood = data.mood;
                scene.add(building);
                return building;
            });
        }

        if (this._config.showVegetation) {
            createForest(scene);
        }
    }

    _initCamera() {
        this._cameraController = new CameraController(
            this._sceneApi.camera,
            this._sceneApi.renderer.domElement,
            this._sceneApi.onFrame.bind(this._sceneApi),
        );
        this._cameraController.setMode(this._config.cameraMode);
    }

    _initInteraction() {
        if (this._config.mode === 'explore') {
            this._tooltipManager = new TooltipManager(
                this._config.container,
                this._config.language,
            );

            this._interactionManager = new InteractionManager(
                this._sceneApi.scene,
                this._sceneApi.camera,
                this._sceneApi.renderer.domElement,
                this._config.container,
                this._buildings,
            );

            this._interactionManager.on('hover', (data) => {
                const label = data.object.userData.emotionLabel;
                if (label) {
                    const text = label[this._config.language] || '';
                    this._tooltipManager.show(text, data.screenPosition);
                }
                this._events.emit('building-hover', {
                    buildingId: data.object.userData.buildingId,
                    name: data.object.userData.name,
                    emotionLabel: data.object.userData.emotionLabel,
                    screenPosition: data.screenPosition,
                });
            });

            this._interactionManager.on('hover-end', () => {
                this._tooltipManager.hide();
                this._events.emit('building-hover-end', {});
            });

            this._interactionManager.on('click', (data) => {
                this._events.emit('location-selected', {
                    worldPosition: data.worldPosition,
                    screenPercent: data.screenPercent,
                    buildingId: data.object.userData.buildingId,
                    label: data.object.userData.name?.[this._config.language] || '',
                    mood: data.object.userData.mood,
                });
            });
        }

        if (this._config.showMarkers || this._config.mode === 'explore') {
            this._markerSystem = new MarkerSystem(this._sceneApi.scene);
        }
    }
}
