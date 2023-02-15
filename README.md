# Treinando o modelo

A técnica de reconhecimento utilizada no projeto é Yolo v5, foi escolhido o modelo yolov5s no qual é um modelo pequeno e recomendado para ser utilizado em computadores com pouco poder computacional e sem aceleração de GPU.

Devido alguns resultados insatisfatório utilizando datasets públicos para treinamento e reconhecimento, foi criado um dataset com algumas imagens publicadas na internet.

Para treinar o modelo, clone o projeto do Yolov5 (https://github.com/ultralytics/yolov5.git) e copie todo o conteúdo do diretório yolov5_to_train, exceto a pasta runs, para dentro do diretório raiz do Yolo e execute o seguinte comando:

python train.py --img 640  --data .\data\mouse_data.yaml --weights yolov5s.pt --epochs 100 --batch-size 4 --name results

No treinamento as imagens do dataset foram redimensionadas para 640x640, utilizado o modelo yolov5 para pesos iniciais, batch-size de 4 imagens e 100 épocas para treinamento.

Após o treinamento, dentro do diretório runs/train/weights criado no yolo, copie o arquivo best.pt para dentro de system_a e renomeie para weights.pt (o resultado do treinamento já se encontra no system_a)

# Executando a API

Dentro do diretório system_b, execute o comando para subir a API:

docker compose up

Pode ocorrer da API tentar conectar no banco antes do banco estar preparado, caso ocorra, encerra a execução atual e execute novamente o compose

# Executando o sistem de detecção

Dentro do diretório system_a, execute o script main.py. As dependências desse projeto são as utilizadas no Yolo, basta instalar os requirements.txt do yolo.

python main.py

