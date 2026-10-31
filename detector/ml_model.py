import os
import logging
import threading
import time
import warnings
import numpy as np
from PIL import Image, ImageOps
from django.conf import settings

logger = logging.getLogger(__name__)

# Suppress standard TensorFlow Lite deprecation notice in logs
warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow.lite")

# Thread-safe global caches for model and labels
_MODEL_CACHE = None
_LABELS_CACHE = None
_MODEL_LOCK = threading.Lock()

# Configurable confidence threshold for low-confidence warnings
LOW_CONFIDENCE_THRESHOLD = 55.0

# Comprehensive knowledge base for plant diseases
DISEASE_INFO = {
    'apple apple scab': {
        'display_name': 'Apple Scab',
        'plant': 'Apple',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Venturia inaequalis',
        'description': 'Apple scab is a prevalent fungal disease affecting apple foliage and fruit, causing olive-green to dark velvety lesions and premature defoliation.',
        'symptoms': [
            'Olive-green to dull dark-brown velvety spots on leaves',
            'Leaf curling, distortion, and premature autumn-like defoliation in midsummer',
            'Corky, cracked, scab-like brown lesions on maturing apple fruit'
        ],
        'causes': 'Fungal ascospores overwintering on fallen leaf litter, released during cool, wet spring rains (13-24°C).',
        'prevention': [
            'Rake and compost or destroy fallen orchard leaves in autumn to eliminate primary spore reservoirs.',
            'Prune tree canopies annually to maximize sunlight penetration and rapid foliage drying.',
            'Plant resistant apple cultivars such as Liberty, Enterprise, or Freedom.'
        ],
        'treatment': [
            'Apply protectant fungicides (captan, mancozeb, or liquid copper) at green tip through petal fall.',
            'Apply systemic fungicides (myclobutanil) if infection periods with prolonged wetting occur.'
        ]
    },
    'apple black rot': {
        'display_name': 'Black Rot (Frogeye Leaf Spot)',
        'plant': 'Apple',
        'is_healthy': False,
        'severity': 'Severe',
        'scientific_name': 'Diplodia seriata (Botryosphaeria obtusa)',
        'description': 'Black rot is a destructive disease that causes frogeye leaf spots on apple foliage, bark cankers on limbs, and firm mummified dark rot on fruit.',
        'symptoms': [
            'Small purple specks on leaves expanding into circular tan lesions with purple margins ("frogeye" spots)',
            'Tiny black fungal fruiting bodies (pycnidia) clustered inside dead leaf spots',
            'Sunken reddish-brown bark cankers on twigs and scaffold limbs',
            'Firm, dark brown to black rot on developing fruit with concentric rings'
        ],
        'causes': 'Overwinters in dead wood, cankered twigs, and mummified fruit left on trees, spreading in warm, humid weather (20-27°C).',
        'prevention': [
            'Prune out dead or cankered branches during dormant winter season and burn or discard them.',
            'Remove all mummified fruits clinging to the tree or lying on the orchard floor.',
            'Maintain optimal tree nutrition and avoid bark wounding from machinery.'
        ],
        'treatment': [
            'Apply captan or thiophanate-methyl sprays from tight cluster through late cover sprays.',
            'Promptly excise new cankers and discard infected leaves.'
        ]
    },
    'apple cedar apple rust': {
        'display_name': 'Cedar Apple Rust',
        'plant': 'Apple',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Gymnosporangium juniperi-virginianae',
        'description': 'A heteroecious fungal disease that requires both apple/crabapple and Eastern red cedar (Juniperus virginiana) to complete its complex two-year life cycle.',
        'symptoms': [
            'Bright yellow-orange or reddish circular spots on the upper leaf surface in late spring',
            'Tiny black raised dots (spermogonia) in the center of yellow foliar spots',
            'Tube-like fungal aecia structures protruding from the underside of leaves in midsummer',
            'Premature leaf shedding causing tree stress and reduced fruit size'
        ],
        'causes': 'Wind-carried basidiospores originating from gelatinous cedar galls during warm spring rains.',
        'prevention': [
            'Remove or prune galls from Eastern red cedar trees growing within 1-2 miles of the orchard.',
            'Plant rust-immune or resistant varieties such as Redfree, Liberty, or Priscilla.',
            'Avoid ornamental plantings of susceptible juniper species near apple trees.'
        ],
        'treatment': [
            'Apply protective fungicides (myclobutanil, mancozeb, or immunox) from pink bud until 2-3 weeks after petal fall.',
            'Fungicide sprays are ineffective once orange foliar lesions have already emerged.'
        ]
    },
    'apple healthy': {
        'display_name': 'Healthy Apple Foliage',
        'plant': 'Apple',
        'is_healthy': True,
        'severity': 'None',
        'scientific_name': 'Malus domestica',
        'description': 'The apple foliage displays uniform vibrant green coloration, crisp intact serrated margins, robust venation, and zero signs of pathogen damage.',
        'symptoms': [
            'Uniform vibrant green color across leaf surface',
            'Intact, clean serrated leaf margins with no chlorosis or necrosis',
            'Smooth, vigorous petiole and healthy vein network'
        ],
        'causes': 'Optimal soil pH (6.0-7.0), balanced fertilization, adequate sunlight, and proper orchard canopy ventilation.',
        'prevention': [
            'Maintain annual dormant pruning for good air circulation and light penetration.',
            'Apply balanced fruit tree fertilizer with adequate calcium and potassium.',
            'Mulch root zones to preserve soil moisture and prevent weed competition.'
        ],
        'treatment': [
            'No treatment needed. Continue good cultural orchard management practices.'
        ]
    },
    'potato early blight': {
        'display_name': 'Early Blight',
        'plant': 'Potato',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Alternaria solani',
        'description': 'Early blight is a fungal disease affecting potato foliage and stems, causing premature defoliation and reduced tuber yield.',
        'symptoms': [
            'Small, dark brown to black spots with concentric rings ("target board" pattern) on older lower leaves',
            'Yellow halo surrounding circular leaf lesions',
            'Leaves eventually turn completely yellow, wither, and drop off',
            'Sunken dark lesions on potato stems near the soil line'
        ],
        'causes': 'Prolonged leaf wetness, warm humid weather (24-29°C), and stress on maturing plants.',
        'prevention': [
            'Practice crop rotation with non-solanaceous crops every 2-3 years.',
            'Ensure adequate plant spacing to allow air circulation and sunlight penetration.',
            'Water at the base using drip irrigation; avoid overhead watering.'
        ],
        'treatment': [
            'Apply copper-based fungicides or chlorothalonil at the first sign of leaf spots.',
            'Remove and safely dispose of infected lower leaves.',
            'Maintain optimal soil nitrogen and potassium levels to reduce plant stress.'
        ]
    },
    'potato late blight': {
        'display_name': 'Late Blight',
        'plant': 'Potato',
        'is_healthy': False,
        'severity': 'Critical',
        'scientific_name': 'Phytophthora infestans',
        'description': 'Late blight is an aggressive oomycete (water mold) disease. It spreads rapidly in cool, wet weather and can destroy an entire field within days.',
        'symptoms': [
            'Water-soaked, pale-green to dark purplish-brown lesions on leaves and stems',
            'White, cottony fungal growth on the underside of leaves during damp conditions',
            'Foul rotting odor in severe infections',
            'Tubers develop dark, sunken, granular rot'
        ],
        'causes': 'Cool, humid weather (10-20°C with relative humidity > 90%) and moisture accumulation on foliage.',
        'prevention': [
            'Plant certified disease-free seed tubers.',
            'Destroy volunteer potato plants and cull piles.',
            'Choose late blight-resistant potato varieties when available.'
        ],
        'treatment': [
            'Apply systemic fungicides (mancozeb, metalaxyl, or cymoxanil) immediately upon notice.',
            'Prune and destroy infected stems and leaves (never compost infected material).',
            'Harvest tubers in dry weather and ensure dry, well-ventilated storage.'
        ]
    },
    'potato healthy': {
        'display_name': 'Healthy Potato Leaf',
        'plant': 'Potato',
        'is_healthy': True,
        'severity': 'None',
        'scientific_name': 'Solanum tuberosum',
        'description': 'The potato leaf displays vibrant green color, strong cellular structure, and no visible signs of pathogen infection or nutrient deficiency.',
        'symptoms': [
            'Uniform green foliage with intact margins',
            'No spots, discoloration, or wilt',
            'Vigorous leaf growth and healthy vein structure'
        ],
        'causes': 'Optimal balance of nutrients, watering, sunlight, and a pathogen-free environment.',
        'prevention': [
            'Maintain a regular watering schedule without waterlogging.',
            'Apply balanced N-P-K fertilizer and inspect leaves weekly.',
            'Keep garden beds mulched to prevent soil splash onto foliage.'
        ],
        'treatment': [
            'No chemical or organic treatment needed. Continue good agricultural practices.'
        ]
    },
    'tomato early blight': {
        'display_name': 'Early Blight',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Alternaria linariae / Alternaria solani',
        'description': 'A frequent fungal disease that attacks tomato leaves, stems, and fruits, typically starting on older foliage near the ground.',
        'symptoms': [
            'Brown to dark brown spots featuring distinctive concentric rings like a target',
            'Tissues surrounding spots turn yellow; leaves may drop prematurely',
            'Stem lesions that can cause collar rot in young seedlings',
            'Leathery sunken spots near the fruit stem'
        ],
        'causes': 'Warm, humid weather (24-30°C) and splashing rain or overhead irrigation transferring spores from soil.',
        'prevention': [
            'Mulch around the base of plants to create a barrier against soil-borne spores.',
            'Prune lower branches (bottom 12 inches) once plants are established.',
            'Rotate tomato crops every 3 seasons away from the nightshade family.'
        ],
        'treatment': [
            'Spray bio-fungicide (Bacillus subtilis) or copper fungicide at initial spotting.',
            'Remove heavily blighted leaves to slow upward progress.',
            'Sanitize garden tools between plants.'
        ]
    },
    'tomato late blight': {
        'display_name': 'Late Blight',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'Critical',
        'scientific_name': 'Phytophthora infestans',
        'description': 'A devastating pathogen that rapidly destroys tomato leaves, vines, and green or ripe fruits, turning plants brown and withered.',
        'symptoms': [
            'Irregular water-soaked greasy lesions turning brown to purplish-black',
            'Fuzzy white fungal growth on leaf undersides in high humidity',
            'Rapid browning and collapse of entire vines',
            'Greasy golden-brown lesions on green tomato fruits'
        ],
        'causes': 'High humidity (>90%) and moderate temperatures (15-22°C) with persistent leaf wetness.',
        'prevention': [
            'Ensure full sun exposure (at least 6-8 hours daily).',
            'Stake or cage tomato plants to keep foliage off the ground.',
            'Avoid working in tomato beds when leaves are wet.'
        ],
        'treatment': [
            'Apply preventative copper or chlorothalonil spray before prolonged wet periods.',
            'Remove infected plants immediately and seal in bags to prevent spore travel.',
            'Do not allow infected material into compost heaps.'
        ]
    },
    'tomato bacterial spot': {
        'display_name': 'Bacterial Spot',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'High',
        'scientific_name': 'Xanthomonas perforans',
        'description': 'A serious bacterial infection that creates numerous tiny spots on leaves and scabby lesions on fruits, reducing fruit quality and yield.',
        'symptoms': [
            'Small (1-3mm), dark brown, water-soaked circular to angular leaf spots',
            'Spots may merge, causing leaves to look scorched and ragged',
            'Yellowing around spots and premature defoliation',
            'Raised, blister-like black spots on green fruit that turn scabby'
        ],
        'causes': 'Warm, rainy, and windy conditions that spread bacteria through water droplets and wounds.',
        'prevention': [
            'Use certified disease-free seeds and transplants.',
            'Avoid overhead sprinklers and working with wet plants.',
            'Disinfect stakes, cages, and pruning shears with 10% bleach solution.'
        ],
        'treatment': [
            'Apply fixed copper bactericide mixed with mancozeb for improved efficacy.',
            'Remove infected leaves early in dry weather.',
            'Rotate fields with non-host crops for at least 2 years.'
        ]
    },
    'tomato leaf mold': {
        'display_name': 'Leaf Mold',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Passalora fulva',
        'description': 'A fungal disease predominantly found in greenhouses or high-humidity tunnels, causing pale yellow spots on upper leaf surfaces and velvety mold beneath.',
        'symptoms': [
            'Pale green or yellowish spots with indefinite margins on upper leaf surfaces',
            'Olive green to velvety purple-brown fungal mold on lower leaf surface',
            'Infected leaves curl, wither, and drop prematurely'
        ],
        'causes': 'Relative humidity above 85% and warm temperatures (21-24°C).',
        'prevention': [
            'Increase greenhouse ventilation and use fans to circulate dry air.',
            'Space plants adequately and prune suckers to improve airflow.',
            'Avoid splashing water on foliage.'
        ],
        'treatment': [
            'Spray approved fungicides (copper octanoate, azoxystrobin) at first notice.',
            'Lower humidity by heating and ventilating greenhouse structures.'
        ]
    },
    'tomato septoria leaf spot': {
        'display_name': 'Septoria Leaf Spot',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Septoria lycopersici',
        'description': 'A destructive fungal disease that causes numerous circular spots with light gray centers and dark borders, starting on lower leaves.',
        'symptoms': [
            'Small (1.5-3mm) circular spots with gray or tan centers and dark brown margins',
            'Tiny black specks (pycnidia fruiting bodies) visible inside center of spots',
            'Leaves turn yellow, shrivel, and fall off rapidly'
        ],
        'causes': 'Wet weather, moderate temperatures (20-25°C), and soil splash.',
        'prevention': [
            'Mulch heavily around the plant base.',
            'Space plants 24-36 inches apart.',
            'Keep weeds under control as some host the fungus.'
        ],
        'treatment': [
            'Apply chlorothalonil, mancozeb, or copper fungicides at 7-10 day intervals.',
            'Remove infected lower foliage promptly.'
        ]
    },
    'tomato spider mites two spotted spider mite': {
        'display_name': 'Spider Mites Infestation',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Tetranychus urticae',
        'description': 'Tiny arachnid pests that pierce plant cells and suck sap, leading to fine stippling, chlorosis, and webbing across leaves.',
        'symptoms': [
            'Fine yellow, white, or bronze speckling (stippling) on leaves',
            'Fine silky webbing on undersides of leaves and between stems',
            'Leaves turn dry, yellow, brittle, and drop off in severe infestations'
        ],
        'causes': 'Hot, dry, and dusty conditions (above 30°C) which accelerate mite reproduction.',
        'prevention': [
            'Regularly mist leaves or irrigate adequately during drought periods.',
            'Preserve natural predators like ladybugs and predatory mites.',
            'Keep dust down along paths and garden borders.'
        ],
        'treatment': [
            'Spray with insecticidal soap, horticultural oil, or neem oil (coat undersides well).',
            'Wash foliage with strong water spray to dislodge mites.',
            'Apply miticide if infestation is severe.'
        ]
    },
    'tomato target spot': {
        'display_name': 'Target Spot',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'Moderate',
        'scientific_name': 'Corynespora cassiicola',
        'description': 'A fungal foliar and fruit pathogen causing brown pinpoint lesions that expand into target-like circular patterns.',
        'symptoms': [
            'Pinpoint brown spots that expand into circular brown lesions with light centers',
            'Zonate concentric rings similar to early blight but often smaller and more numerous',
            'Large brown sunken lesions on ripe fruit'
        ],
        'causes': 'Warm, humid tropical and subtropical climates with frequent rain.',
        'prevention': [
            'Avoid excessive nitrogen fertilization which produces overly dense canopies.',
            'Remove crop debris after harvesting.',
            'Use drip irrigation.'
        ],
        'treatment': [
            'Apply broad-spectrum fungicides such as azoxystrobin or chlorothalonil.',
            'Improve row spacing to promote faster leaf drying.'
        ]
    },
    'tomato tomato yellow leaf curl virus': {
        'display_name': 'Yellow Leaf Curl Virus',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'High',
        'scientific_name': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
        'description': 'A devastating viral disease transmitted by the silverleaf whitefly (Bemisia tabaci), causing stunted bushy growth and severe yield loss.',
        'symptoms': [
            'Severe upward curling and cupping of leaf margins',
            'Yellowing (chlorosis) of leaf margins while inner leaf remains green',
            'Leaves become noticeably smaller and puckered',
            'Plant exhibits stunted bushy growth and flowers drop without setting fruit'
        ],
        'causes': 'Spread by whiteflies feeding on infected weeds or crops.',
        'prevention': [
            'Use yellow sticky traps to monitor and catch whiteflies.',
            'Plant TYLCV-resistant tomato cultivars.',
            'Use fine mesh insect netting in nurseries and greenhouse tunnels.'
        ],
        'treatment': [
            'There is no cure for viral infection; remove and destroy infected plants immediately.',
            'Control whitefly populations using neem oil, insecticidal soap, or approved insecticides.'
        ]
    },
    'tomato tomato mosaic virus': {
        'display_name': 'Tomato Mosaic Virus',
        'plant': 'Tomato',
        'is_healthy': False,
        'severity': 'High',
        'scientific_name': 'Tomato mosaic virus (ToMV)',
        'description': 'A highly contagious and resilient virus that causes mottled green/yellow patches on leaves and distortion of new foliage.',
        'symptoms': [
            'Mottling with alternating light and dark green patches on leaves',
            'Leaves distorted, blistered, or narrowed into "shoestring" or "fern-like" shapes',
            'Stunted plant growth and uneven fruit ripening with internal browning'
        ],
        'causes': 'Transmitted mechanically through hands, tools, smoking tobacco contact, and contaminated seeds.',
        'prevention': [
            'Wash hands thoroughly with soap or milk solution before handling plants.',
            'Do not smoke or use tobacco products near tomato gardens.',
            'Disinfect tools in 20% nonfat dry milk or bleach solution.'
        ],
        'treatment': [
            'No chemical cure exists for viral plant infections.',
            'Carefully dig up and bag/burn infected plants.',
            'Avoid planting tomatoes in the same spot for at least two seasons.'
        ]
    },
    'tomato healthy': {
        'display_name': 'Healthy Tomato Leaf',
        'plant': 'Tomato',
        'is_healthy': True,
        'severity': 'None',
        'scientific_name': 'Solanum lycopersicum',
        'description': 'The tomato leaf shows lush green foliage, crisp leaf edges, robust veins, and zero sign of fungal, bacterial, viral, or pest damage.',
        'symptoms': [
            'Uniform vibrant green color across leaflets',
            'No spots, curling, lesions, or wilting',
            'Smooth surface with characteristic fine natural glandular hairs'
        ],
        'causes': 'Optimal soil pH (6.0-6.8), consistent moisture, sunlight, and proper nutrient levels.',
        'prevention': [
            'Maintain regular deep watering at soil level.',
            'Apply balanced tomato fertilizer with calcium to prevent blossom end rot.',
            'Prune lower suckers for good air movement and light distribution.'
        ],
        'treatment': [
            'No treatment required. The tomato plant is thriving and healthy.'
        ]
    }
}


def load_labels(labels_path=None):
    """
    Loads class labels from labels_demo.txt or labels.txt with caching.
    """
    global _LABELS_CACHE
    if _LABELS_CACHE is not None:
        return _LABELS_CACHE

    if labels_path is None:
        demo_labels = os.path.join(settings.BASE_DIR, 'models', 'labels_demo.txt')
        default_labels = os.path.join(settings.BASE_DIR, 'models', 'labels.txt')
        labels_path = demo_labels if os.path.exists(demo_labels) else default_labels

    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"Labels file not found at: {labels_path}")

    with open(labels_path, 'r', encoding='utf-8') as f:
        labels = [line.strip().lower() for line in f.readlines() if line.strip()]

    _LABELS_CACHE = labels
    return _LABELS_CACHE


def load_model_instance():
    """
    Thread-safe singleton model loader for fast inference.
    Reuses existing model interpreter across requests.
    Prioritizes demo model (plant_disease_demo.tflite / .keras) if present.
    Returns:
        tuple: (model_type, model_instance, input_index, output_index, lock)
    """
    global _MODEL_CACHE
    with _MODEL_LOCK:
        if _MODEL_CACHE is not None:
            return _MODEL_CACHE

        demo_tflite = os.path.join(settings.BASE_DIR, 'models', 'plant_disease_demo.tflite')
        demo_keras = os.path.join(settings.BASE_DIR, 'models', 'plant_disease_demo.keras')
        tflite_path = demo_tflite if os.path.exists(demo_tflite) else os.path.join(settings.BASE_DIR, 'models', 'plant_disease_model.tflite')
        keras_path = demo_keras if os.path.exists(demo_keras) else os.path.join(settings.BASE_DIR, 'models', 'plant_disease_model.keras')

        # Prioritize trained TFLite model for speed and minimal memory
        if os.path.exists(tflite_path):
            import tensorflow as tf
            interpreter = tf.lite.Interpreter(model_path=tflite_path)
            interpreter.allocate_tensors()
            in_details = interpreter.get_input_details()
            out_details = interpreter.get_output_details()
            input_idx = in_details[0]['index']
            output_idx = out_details[0]['index']
            infer_lock = threading.Lock()
            _MODEL_CACHE = ('tflite', interpreter, input_idx, output_idx, infer_lock)
            return _MODEL_CACHE

        elif os.path.exists(keras_path):
            import tensorflow as tf
            model = tf.keras.models.load_model(keras_path)
            infer_lock = threading.Lock()
            _MODEL_CACHE = ('keras', model, None, None, infer_lock)
            return _MODEL_CACHE

        else:
            raise FileNotFoundError(
                f"No trained model found. Expected either {tflite_path} or {keras_path}."
            )


def preprocess_image(image_input, target_size=(224, 224)):
    """
    Efficiently preprocesses an uploaded image:
    1. Opens with Pillow and auto-rotates via EXIF tag if needed.
    2. Converts to standard 3-channel RGB.
    3. Resizes to target dimension (224x224) using bilinear interpolation.
    4. Normalizes to float32 pixels.
    5. Returns batch tensor of shape [1, 224, 224, 3].
    """
    opened_locally = False
    if hasattr(image_input, 'read'):
        image = Image.open(image_input)
    elif isinstance(image_input, str):
        image = Image.open(image_input)
        opened_locally = True
    elif isinstance(image_input, Image.Image):
        image = image_input
    else:
        raise ValueError("Unsupported image input type.")

    try:
        # Correct orientation from mobile EXIF data if present
        image = ImageOps.exif_transpose(image)

        # Convert to RGB (handles transparency, CMYK, grayscale)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize to model input dimensions
        image_resized = image.resize(target_size, Image.Resampling.BILINEAR)

        # Convert to float32 array in [0, 255] for MobileNetV2 with internal preprocess_input
        img_array = np.array(image_resized, dtype=np.float32)

        # Expand batch dimension
        img_batch = np.expand_dims(img_array, axis=0)
        return img_batch
    finally:
        if opened_locally:
            image.close()


def predict_disease(image_path_or_file, selected_plant='tomato'):
    """
    Executes ML inference on an image and returns:
    - raw_class: Exact label from model
    - display_name: Human-friendly disease title
    - selected_plant: User-selected plant ('Tomato' or 'Potato')
    - confidence: Confidence percentage (0-100)
    - top_3: Top 3 class predictions with confidence percentages
    - is_plant_match: Whether predicted class belongs to user-selected plant
    - warning_message: Informative warning if mismatch or low confidence
    - disease_info: Dictionary containing symptoms, causes, prevention, treatment
    - inference_time_ms: Measured latency in milliseconds
    """
    t_start = time.perf_counter()

    model_type, model_instance, input_idx, output_idx, infer_lock = load_model_instance()
    labels = load_labels()

    # Preprocess image
    input_data = preprocess_image(image_path_or_file, target_size=(224, 224))

    # Thread-safe inference execution
    with infer_lock:
        if model_type == 'tflite':
            model_instance.set_tensor(input_idx, input_data)
            model_instance.invoke()
            predictions = model_instance.get_tensor(output_idx)[0]
        elif model_type == 'keras':
            predictions = model_instance.predict(input_data, verbose=0)[0]

    # Ensure softmax probabilities
    if np.sum(predictions) > 0:
        predictions = predictions / np.sum(predictions)

    sorted_indices = np.argsort(predictions)[::-1]
    top_idx = sorted_indices[0]
    predicted_raw = labels[top_idx]
    confidence_pct = round(float(predictions[top_idx]) * 100, 2)

    # Top 3 predictions breakdown
    top_3 = []
    for idx in sorted_indices[:3]:
        raw_name = labels[idx]
        conf = round(float(predictions[idx]) * 100, 2)
        info = DISEASE_INFO.get(raw_name)
        display_label = info['display_name'] if info else raw_name.replace('___', ' - ').replace('_', ' ').title()
        top_3.append({
            'raw_name': raw_name,
            'display_name': display_label,
            'confidence': conf
        })

    # Validate crop match
    selected_plant_lower = selected_plant.lower().strip()
    predicted_plant_is_selected = selected_plant_lower in predicted_raw

    # Find closest match specifically for the selected plant
    selected_plant_indices = [
        i for i in sorted_indices if selected_plant_lower in labels[i]
    ]

    selected_plant_top = None
    if selected_plant_indices:
        best_plant_idx = selected_plant_indices[0]
        selected_plant_top = {
            'raw_name': labels[best_plant_idx],
            'confidence': round(float(predictions[best_plant_idx]) * 100, 2)
        }

    warning_message = None
    is_plant_match = True

    # Reliability evaluation
    if not predicted_plant_is_selected:
        is_plant_match = False
        detected_plant_name = predicted_raw.split()[0].title()
        warning_message = (
            f"Crop Mismatch Notice: You selected '{selected_plant.title()}', but the model identified "
            f"visual features matching '{detected_plant_name}' ({predicted_raw.title()}) with {confidence_pct}% confidence. "
            f"If this is indeed a {selected_plant.title()} leaf, the closest matching {selected_plant.title()} diagnosis is shown below."
        )
    elif confidence_pct < LOW_CONFIDENCE_THRESHOLD:
        warning_message = (
            f"Low Confidence Estimate: The model's confidence is {confidence_pct}%. "
            "Lighting, background clutter, or leaf angle may affect prediction accuracy. "
            "Please verify visually and consult an agricultural expert."
        )

    # Look up details
    lookup_key = predicted_raw if predicted_plant_is_selected else (
        selected_plant_top['raw_name'] if selected_plant_top else predicted_raw
    )
    disease_details = DISEASE_INFO.get(lookup_key, {
        'display_name': lookup_key.replace('_', ' ').title(),
        'plant': selected_plant.title(),
        'is_healthy': 'healthy' in lookup_key,
        'severity': 'Moderate' if 'healthy' not in lookup_key else 'None',
        'scientific_name': 'Solanum species',
        'description': f'Disease diagnosis identified as {lookup_key.replace("_", " ").title()}.',
        'symptoms': ['Visible foliage lesions or discoloration.'],
        'causes': 'Pathogen presence under favorable humidity/temperature conditions.',
        'prevention': ['Inspect plants regularly and remove dead or diseased foliage.'],
        'treatment': ['Consult local agricultural extension for recommended treatment.']
    })

    t_end = time.perf_counter()
    inference_time_ms = round((t_end - t_start) * 1000, 2)

    return {
        'raw_class': predicted_raw,
        'display_name': disease_details['display_name'],
        'selected_plant': selected_plant.title(),
        'confidence': confidence_pct,
        'top_3': top_3,
        'is_plant_match': is_plant_match,
        'warning_message': warning_message,
        'disease_info': disease_details,
        'selected_plant_top': selected_plant_top,
        'inference_time_ms': inference_time_ms,
    }
