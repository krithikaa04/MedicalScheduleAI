    ```mermaid
flowchart LR
    %% Define styles with refined colors and styling
    classDef dataBlock fill:#d0e8f2,stroke:#2874A6,stroke-width:2px,color:#1A5276,rounded:true
    classDef processBlock fill:#d4efdf,stroke:#239B56,stroke-width:2px,color:#186A3B,rounded:true
    classDef modelBlock fill:#fdebd0,stroke:#CA6F1E,stroke-width:2px,color:#9C640C,rounded:true,font-weight:bold
    classDef collatorBlock fill:#ebdef0,stroke:#8E44AD,stroke-width:2px,color:#6C3483,rounded:true
    classDef outputBlock fill:#FCF3CF,stroke:#D4AC0D,stroke-width:3px,color:#9A7D0A,rounded:true,font-weight:bold
    classDef mainProcess fill:#FDFEFE,stroke:#2C3E50,stroke-width:3px,color:#2C3E50,rounded:true,font-weight:bold
    
    %% Data Preparation
    subgraph DataPrep["1. Data Preparation"]
        direction TB
        A[".npy Audio Files"] --> |"paired with"| B["transcriptions.txt"]
        A & B --> C["load_npy_data()"]
        C --> D["HuggingFace Dataset"]
    end
    
    %% Data Preprocessing
    subgraph DataProcess["2. Data Preprocessing"]
        direction TB
        E["preprocess_data()"] --> G["Processed Dataset with Features & Labels"]
        G --> H["Train/Test Split (90/10)"]
        F["Wav2Vec2Processor"] --> |"processes audio & text"| E
    end
    
    %% Custom Collator
    subgraph Collator["3. CTC Data Collator"]
        direction TB
        I["CTCDataCollator Class"] --> J["Batch Preparation"]
        J --> K["Handle Variable-Length Sequences"]
        K --> L["Mask Padding for CTC Loss"]
    end
    
    %% Model Architecture
    subgraph ModelArch["4. Wav2Vec2 Architecture"]
        direction TB
        S["CNN Feature Encoder"] --> |"extracts features"| T["Transformer Encoder"]
        T --> |"contextual representation"| U["CTC Output Layer"]
    end
    
    %% Training Setup & Process
    subgraph Training["5. Training Pipeline"]
        direction TB
        M["TrainingArguments"] --> |"configures"| N["Trainer"]
        O["Pretrained Wav2Vec2ForCTC\nfacebook/wav2vec2-base-960h"] --> |"initialize"| N
        N --> P["Training Loop (3 epochs)"]
        P --> Q["Periodic Evaluation"]
        Q --> R["Save Checkpoints"]
    end
    
    %% Final Output
    subgraph Output["6. Final Output"]
        direction TB
        V["Fine-tuned Wav2Vec2 Model"] 
        W["Saved Processor for Inference"]
    end
    
    %% Main Flow Connection with cleaner connections
    DataPrep --> |"processed data"| DataProcess
    DataProcess --> |"train & test sets"| Training
    Collator --> |"batching strategy"| Training
    ModelArch --> |"model architecture"| O
    Training --> |"produces"| Output
    
    %% Apply styles
    class A,B,D,G,H dataBlock
    class C,E,J,K,L,P,Q processBlock
    class F,O,S,T,U modelBlock
    class I,M,N collatorBlock
    class R,V,W outputBlock
    class DataPrep,DataProcess,Collator,ModelArch,Training,Output mainProcess
```