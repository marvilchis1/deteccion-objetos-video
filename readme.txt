1.- Crear un entorno virtual en Python y activarlo
	python -m venv work
	source work/bin/activate

2.- Instalar opencv (version normal en Ubuntu, headless para Mac OS)

3.- Instalar torch

4.- Instalar xvfb (solo si se ejecutara en Ubuntu)

5.- Instalar pandas

6.- Ejecutar el siguiente comando para instalar las ademas librerías necesarias:
	pip install -r requirements.txt

7.- Una vez instalado todo, con chmod darle todos los permisos al script getdata.sh

8.- Ejecucion del script:
	./getdata.sh <nombre_video.mp4>

9.- Como resultado se obtiene:
	* results.csv 	— Archivo csv enlistando todos los objetos coincidentes.
	* outvideo.mp4	— Video dcon los bounding boxes.