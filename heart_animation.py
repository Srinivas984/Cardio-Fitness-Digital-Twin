
import streamlit.components.v1 as components
import base64

def show_beating_heart(heart_rate):

    # convert model to base64
    with open("heart.glb", "rb") as f:
        model_data = base64.b64encode(f.read()).decode()

    beat_speed = max(0.6, min(2.0, heart_rate / 70))

    html_code = f"""
    <html>
    <head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128/examples/js/loaders/GLTFLoader.js"></script>
    </head>

    <body style="margin:0;background:#050b1a">

    <div id="container"></div>

    <script>

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(75, 600/400, 0.1, 1000);

    const renderer = new THREE.WebGLRenderer({{antialias:true}});
    renderer.setSize(600,400);

    document.getElementById("container").appendChild(renderer.domElement);

    const light1 = new THREE.PointLight(0xffffff,1.5);
    light1.position.set(5,5,5);
    scene.add(light1);

    const light2 = new THREE.AmbientLight(0x404040);
    scene.add(light2);

    const loader = new THREE.GLTFLoader();

    const modelData = "data:model/gltf-binary;base64,{model_data}";

    let heart;

    loader.load(
        modelData,
        function(gltf) {{
            heart = gltf.scene;
            heart.scale.set(3,3,3);
            scene.add(heart);
        }},
        undefined,
        function(error) {{
            console.error(error);
        }}
    );

    camera.position.z = 10;

    function animate() {{

        requestAnimationFrame(animate);

        if(heart) {{

            let beat = 1 + Math.sin(Date.now()*0.005*{beat_speed})*0.12;

            heart.scale.set(beat*3,beat*3,beat*3);

            heart.rotation.y += 0.01;
        }}

        renderer.render(scene,camera);
    }}

    animate();

    </script>

    </body>
    </html>
    """

    components.html(html_code,height=420)
