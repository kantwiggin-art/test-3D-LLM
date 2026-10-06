window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('renderCanvas');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const speedVal = document.getElementById('speedVal');
    const statusVal = document.getElementById('statusVal');

    // Initialize Babylon Engine
    const engine = new BABYLON.Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true });

    const createScene = function() {
        const scene = new BABYLON.Scene(engine);

        // Psychedelic Dark Purple Ambient Fog & Background
        scene.clearColor = new BABYLON.Color4(0.08, 0.02, 0.15, 1.0);
        scene.fogMode = BABYLON.Scene.FOGMODE_EXP2;
        scene.fogColor = new BABYLON.Color3(0.12, 0.02, 0.22);
        scene.fogDensity = 0.015;

        // Camera setup (Third-person follow camera)
        const camera = new BABYLON.FollowCamera("FollowCam", new BABYLON.Vector3(0, 5, -10), scene);
        camera.radius = 7.5;
        camera.heightOffset = 2.8;
        camera.rotationOffset = 180;
        camera.cameraAcceleration = 0.08;
        camera.maxCameraSpeed = 20;
        camera.attachControl(canvas, true);

        // Lights
        const hemiLight = new BABYLON.HemisphericLight("HemiLight", new BABYLON.Vector3(0, 1, 0), scene);
        hemiLight.intensity = 0.8;
        hemiLight.diffuse = new BABYLON.Color3(1.0, 0.8, 0.9); // Soft magenta tint
        hemiLight.groundColor = new BABYLON.Color3(0.0, 0.8, 0.9); // Cyan ground reflection

        const dirLight = new BABYLON.DirectionalLight("DirLight", new BABYLON.Vector3(-1, -2, -1), scene);
        dirLight.position = new BABYLON.Vector3(20, 40, 20);
        dirLight.intensity = 1.3;
        dirLight.diffuse = new BABYLON.Color3(1.0, 0.6, 0.3); // Warm desert sunlight

        // Psychedelic Ground Grid
        const ground = BABYLON.MeshBuilder.CreateGround("ground", { width: 300, height: 300, subdivisions: 60 }, scene);
        const groundMat = new BABYLON.StandardMaterial("groundMat", scene);
        groundMat.diffuseColor = new BABYLON.Color3(0.05, 0.01, 0.1);
        groundMat.specularColor = new BABYLON.Color3(0.5, 0.0, 0.8);
        groundMat.wireframe = true; // Neon synthwave/psychedelic grid mesh
        groundMat.emissiveColor = new BABYLON.Color3(0.2, 0.0, 0.4);
        ground.material = groundMat;

        // Psychedelic Glowing Floating Monoliths & Geometric Pillars
        const monolithColors = [
            new BABYLON.Color3(1.0, 0.0, 0.5), // Neon Magenta
            new BABYLON.Color3(0.0, 1.0, 0.9), // Cyan
            new BABYLON.Color3(0.9, 0.9, 0.0), // Gold/Yellow
            new BABYLON.Color3(0.6, 0.0, 1.0)  // Vivid Purple
        ];

        const floatingObjects = [];

        for (let i = 0; i < 40; i++) {
            const height = Math.random() * 8 + 4;
            const monolith = BABYLON.MeshBuilder.CreateCylinder(`monolith_${i}`, {
                diameterTop: Math.random() * 1.5 + 0.5,
                diameterBottom: Math.random() * 2.5 + 1.0,
                height: height,
                tessellation: 7 // 7-pointed / 7-sided polygon shape inspired by the token
            }, scene);

            const angle = Math.random() * Math.PI * 2;
            const dist = Math.random() * 90 + 15;
            monolith.position.x = Math.cos(angle) * dist;
            monolith.position.z = Math.sin(angle) * dist;
            monolith.position.y = Math.random() * 3 + height / 2;

            const mat = new BABYLON.StandardMaterial(`monolithMat_${i}`, scene);
            const color = monolithColors[i % monolithColors.length];
            mat.diffuseColor = color;
            mat.emissiveColor = color.scale(0.6);
            mat.specularColor = new BABYLON.Color3(1, 1, 1);
            monolith.material = mat;

            floatingObjects.push({ mesh: monolith, baseY: monolith.position.y, speed: Math.random() * 0.02 + 0.01, rotSpeed: Math.random() * 0.02 - 0.01 });
        }

        // Particle System for Psychedelic Dust
        const particleSystem = new BABYLON.ParticleSystem("particles", 1000, scene);
        particleSystem.particleTexture = new BABYLON.Texture("https://raw.githubusercontent.com/BabylonJS/Babylon.js/master/packages/tools/playground/public/textures/flare.png", scene);
        particleSystem.emitter = new BABYLON.Vector3(0, 2, 0);
        particleSystem.minEmitBox = new BABYLON.Vector3(-60, 0, -60);
        particleSystem.maxEmitBox = new BABYLON.Vector3(60, 10, 60);
        particleSystem.color1 = new BABYLON.Color4(0.0, 1.0, 0.9, 0.8);
        particleSystem.color2 = new BABYLON.Color4(1.0, 0.0, 0.8, 0.8);
        particleSystem.colorDead = new BABYLON.Color4(0, 0, 0.2, 0.0);
        particleSystem.minSize = 0.1;
        particleSystem.maxSize = 0.5;
        particleSystem.minLifeTime = 2.0;
        particleSystem.maxLifeTime = 5.0;
        particleSystem.emitRate = 200;
        particleSystem.blendMode = BABYLON.ParticleSystem.BLENDMODE_ONEONE;
        particleSystem.gravity = new BABYLON.Vector3(0, 0.1, 0);
        particleSystem.start();

        // Load Hoverbike V2 GLB Asset
        let bikeMesh = null;
        let bikeRoot = new BABYLON.TransformNode("bikeRoot", scene);

        // Movement State
        const inputMap = {};
        scene.actionManager = new BABYLON.ActionManager(scene);

        scene.actionManager.registerAction(new BABYLON.ExecuteCodeAction(BABYLON.ActionManager.OnKeyDownTrigger, (evt) => {
            inputMap[evt.sourceEvent.key.toLowerCase()] = true;
        }));

        scene.actionManager.registerAction(new BABYLON.ExecuteCodeAction(BABYLON.ActionManager.OnKeyUpTrigger, (evt) => {
            inputMap[evt.sourceEvent.key.toLowerCase()] = false;
        }));

        let speed = 0;
        let rotation = 0;
        const maxSpeed = 0.35;
        const accel = 0.008;
        const friction = 0.96;
        const turnSpeed = 0.035;

        BABYLON.SceneLoader.ImportMeshAsync("", "../hoverbike_v2/", "hoverbike_v2.glb", scene).then((result) => {
            bikeMesh = result.meshes[0];
            bikeMesh.parent = bikeRoot;

            // Orient model so front faces forward (-Z direction for follow camera)
            bikeMesh.rotation = new BABYLON.Vector3(0, Math.PI, 0);
            bikeMesh.position = new BABYLON.Vector3(0, 0, 0);

            camera.lockedTarget = bikeRoot;

            // Hide loading overlay
            if (loadingOverlay) {
                loadingOverlay.style.opacity = '0';
                setTimeout(() => { loadingOverlay.style.display = 'none'; }, 500);
            }
        }).catch(err => {
            console.error("Error loading hoverbike GLB:", err);
        });

        // Animation Loop & Physics Logic
        let time = 0;
        scene.registerBeforeRender(() => {
            time += 0.03;

            // Animate floating monoliths
            floatingObjects.forEach(obj => {
                obj.mesh.position.y = obj.baseY + Math.sin(time * obj.speed * 5) * 0.8;
                obj.mesh.rotation.y += obj.rotSpeed;
            });

            // Animate ground color hue shift
            groundMat.emissiveColor = new BABYLON.Color3(
                0.2 + Math.sin(time * 0.5) * 0.1,
                0.0,
                0.3 + Math.cos(time * 0.5) * 0.1
            );

            if (bikeRoot) {
                // Hover bobbing effect
                const hoverY = 0.6 + Math.sin(time * 2.5) * 0.12;
                bikeRoot.position.y = hoverY;

                // Controls: W / Up
                if (inputMap["w"] || inputMap["arrowup"]) {
                    speed = Math.min(speed + accel, maxSpeed);
                } else if (inputMap["s"] || inputMap["arrowdown"]) {
                    speed = Math.max(speed - accel, -maxSpeed * 0.5);
                } else {
                    speed *= friction;
                }

                // Controls: A/D or Left/Right
                if (inputMap["a"] || inputMap["arrowleft"]) {
                    rotation -= turnSpeed;
                }
                if (inputMap["d"] || inputMap["arrowright"]) {
                    rotation += turnSpeed;
                }

                // Update transform
                bikeRoot.rotation.y = rotation;
                const forward = new BABYLON.Vector3(
                    Math.sin(rotation) * speed,
                    0,
                    Math.cos(rotation) * speed
                );
                bikeRoot.position.addInPlace(forward);

                // Banking tilt when turning
                let targetRoll = 0;
                if (inputMap["a"] || inputMap["arrowleft"]) targetRoll = -0.25;
                if (inputMap["d"] || inputMap["arrowright"]) targetRoll = 0.25;

                if (bikeMesh) {
                    bikeMesh.rotation.z = BABYLON.Scalar.Lerp(bikeMesh.rotation.z, targetRoll, 0.1);
                }

                // HUD updates
                if (speedVal) speedVal.innerText = (Math.abs(speed) * 30).toFixed(2);
                if (statusVal) {
                    if (Math.abs(speed) > 0.05) {
                        statusVal.innerText = "CRUISING";
                        statusVal.style.color = "#00ffaa";
                    } else {
                        statusVal.innerText = "HOVERING";
                        statusVal.style.color = "#ffff00";
                    }
                }
            }
        });

        return scene;
    };

    const scene = createScene();

    engine.runRenderLoop(() => {
        scene.render();
    });

    window.addEventListener('resize', () => {
        engine.resize();
    });
});
