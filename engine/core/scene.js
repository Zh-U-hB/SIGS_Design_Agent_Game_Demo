import * as THREE from 'three';

export function createScene(container) {
    const scene = new THREE.Scene();

    const width = container.clientWidth;
    const height = container.clientHeight;

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(50, 40, 50);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({
        antialias: true,
        preserveDrawingBuffer: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;

    container.appendChild(renderer.domElement);

    const callbacks = [];
    let animationId = null;
    let running = false;

    function animate() {
        if (!running) return;
        animationId = requestAnimationFrame(animate);

        for (const cb of callbacks) {
            cb();
        }

        renderer.render(scene, camera);
    }

    function onFrame(callback) {
        callbacks.push(callback);
    }

    function start() {
        running = true;
        animate();
    }

    function stop() {
        running = false;
        if (animationId !== null) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    }

    function handleResize() {
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    }

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    function destroy() {
        stop();
        resizeObserver.disconnect();
        renderer.dispose();
        if (renderer.domElement.parentNode) {
            renderer.domElement.parentNode.removeChild(renderer.domElement);
        }
    }

    return {
        scene,
        camera,
        renderer,
        onFrame,
        start,
        stop,
        destroy,
    };
}
