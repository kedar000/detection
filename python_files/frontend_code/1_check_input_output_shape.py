from tensorflow.keras.models import load_model

MODEL_PATH = "../keystroke_dataset/gru_overlay_detection_best.keras"

model = load_model(MODEL_PATH)

print("\n==============================")
print("MODEL INFORMATION")
print("==============================")

print("Input shape :", model.input_shape)
print("Output shape:", model.output_shape)

print("\nModel summary:")
model.summary()

print("\nLayers:")
for i, layer in enumerate(model.layers):
    print(
        i,
        "|",
        layer.name,
        "|",
        layer.__class__.__name__,
        "| input:",
        getattr(layer, "input_shape", "N/A"),
        "| output:",
        getattr(layer, "output_shape", "N/A")
    )