import gradio as gr
from typing import Dict, Any

def classify_traffic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify network traffic using the ML model.
    
    Args:
        data: Network traffic data in dictionary format
    
    Returns:
        Dictionary containing classification results
    """
    # TODO: Implement model prediction
    return {
        "prediction": "normal",  # Placeholder
        "confidence": 0.95,      # Placeholder
        "details": data          # Echo input for now
    }

# Create Gradio interface
interface = gr.Interface(
    fn=classify_traffic,
    inputs=gr.JSON(label="Network Traffic Data"),
    outputs=[
        gr.Textbox(label="Prediction"),
        gr.Number(label="Confidence"),
        gr.JSON(label="Details")
    ],
    title="Intrusion Detection System",
    description="Classify network traffic as malicious or normal",
    examples=[
        {"source_ip": "192.168.1.1", "destination_ip": "10.0.0.1", "protocol": "TCP", "port": 80}
    ]
)

if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860) 