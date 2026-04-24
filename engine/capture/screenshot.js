export function captureScreenshot(renderer, scene, camera) {
    return new Promise((resolve) => {
        renderer.render(scene, camera);
        const dataURL = renderer.domElement.toDataURL('image/png');
        resolve(dataURL);
    });
}
