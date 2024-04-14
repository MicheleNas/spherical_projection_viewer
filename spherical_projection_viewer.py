import numpy as np
import cv2
import argparse

# Inizializzazione degli angoli di rotazione.
# Potranno essere modificati tramite i tasti A, W, D, S
phi_rot = 0
theta_rot = 0

# Inizializzazione del fattore di zoom
# Potrà essere modificato tramite i tasti +, -
zoom_factor = 1

# Definizione delle funzioni che generano le matrici di rotazione lungo i due assi y e z
def Ry(theta):
  return np.matrix([[ np.cos(theta), 0, np.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-np.sin(theta), 0, np.cos(theta)]])
 
def Rz(phi):
  return np.matrix([[ np.cos(phi), -np.sin(phi), 0 ],
                   [ np.sin(phi), np.cos(phi) , 0 ],
                   [ 0           , 0            , 1 ]])


# La seguente funzione genera il piano canonico tangente alla sfera considerando come punto
# del piano tangente p = (1,0,0)

# Quindi genera una griglia di punti nello spazio che rappresenta una PROIEZIONE della
# porzione della sfera tangente al piano.La griglia è memorizzata in un array
# multidimensionale di dimensione (H, W, 3)

# La sfera sarà proiettata attraverso un campo visivo espresso dagli angoli 'a_h' e 'a_w'.
def gen_Canonic_Plane(a_w):

    # Definizione delle dimensioni dell'immagine nel piano canonico
    H = 500
    W = H * 16//9

    # Angoli del cono di visuale, assumendo che la distanza focale f = 1
    a_h = 2 * np.arctan((H/W) * np.tan(a_w/2))

    # Definizione di vettori di coordinate x e y
    x = np.array([1])
    y = np.linspace(-W/2, W/2, W)
    z = np.linspace(H/2, -H/2, H)

    # Generazione delle coordinate che insieme definiscono una griglia di punti per x, y e z
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Scalatura dei valori per adattare la griglia di punti generata al 
    # campo visivo specificato da 'a_w' e 'a_h'
    Y = (Y/(W/2)) * np.tan(a_w /2)
    Z = (Z/(H/2)) * np.tan(a_h /2)

    # Combina le matrici X, Y e Z in un unico array tridimensionale in modo 
    # da generare la GRIGLIA DI PUNTI di proiezione
    canonic_plane = np.stack((X, Y, Z), axis=-1).squeeze()

    return canonic_plane


# La funzione 'equi_to_planar()' permette di trasformare un sistema di coordinate equirrettangolari a 
# un sistema di coordinate planari, permettendo anche l'applicazione della rotazione sferica.

# Per farlo tiene in considerazione come piano di partenza il piano canonico calcolato tramite 
# 'gen_canonic_plane()' rappresentato dalla variabile 'canonic_plane', e applicando a questo, qualora 
# fosse richiesto, una rotazione mediante gli angoli 'phi_rot' e 'theta_rot'
def equi_to_planar(canonic_plane, H_img_input, W_img_input):
    global phi_rot, theta_rot, zoom_factor

    # Calcolo del valore di scaling basato sul fattore di zoom
    s = 1 / zoom_factor

    # Generazione della matrice di scaling
    S = np.diag([1, s, s])

    # ZOOM
    canonic_plane_zoom = np.matmul(canonic_plane, S)

    # Generazione della MATRICE DI ROTAZIONE
    R = np.array(Rz(phi_rot) * Ry(theta_rot))

    # ROTAZIONE
    canonic_plane_rotated = np.matmul(canonic_plane_zoom, R.T)

    # Calcolo della NORMA per ogni punto del piano
    norms = np.linalg.norm(canonic_plane_zoom, axis=2, keepdims=True)

    # NORMALIZZAZIONE dei vettori.
    # In questo modo troviamo i punti della sfera 'Ps' conoscendo i punti 'Pi' che
    # rappresentano la proiezione sul piano tangente
    vectors_normalized = canonic_plane_rotated / norms

    # Estrazione di matrici X, Y e Z.
    norm_X = vectors_normalized[:, :, 0]
    norm_Y = vectors_normalized[:, :, 1]
    norm_Z = vectors_normalized[:, :, 2]

    # Calcolo delle coordinate polari, assumendo raggio = 1
    phi = np.arctan2(norm_Y, norm_X)
    theta = np.arccos(norm_Z)

    # Calcolo delle coordinate equirettangolari conoscendo phi e theta (coordinate polari della sfera).
    map_x = (phi + np.pi) * W_img_input/(2 * np.pi)
    map_y = theta * H_img_input/np.pi

    map_x = map_x.astype(np.float32)
    map_y = map_y.astype(np.float32)

    return map_x.T, map_y.T


# Funzione per gestire gli spostamenti (ovvero le rotazioni del piano intorno alla sfera).
def handle_keyboard_input(key):
    global phi_rot, theta_rot, zoom_factor 
    
    # Verso l'alto
    if key == 119 or key == 87:
        theta_rot -= 0.1  
    # Verso il basso
    elif key == 115 or key == 83:
        theta_rot += 0.1  
    # Verso sinistra
    elif key == 97 or key == 65:
        phi_rot -= 0.1
    # Verso destra
    elif key == 100 or key == 75:
        phi_rot += 0.1
    # Zoom +
    elif key == 43 and zoom_factor < 2.9:
        zoom_factor += 0.1
    # Zoom -
    elif key == 45 and zoom_factor > 0.2:
        zoom_factor -= 0.1
    


def main(args):
    global phi_rot, theta_rot

    # Conversione della latitudine, longitudine e fov in radianti
    latitude, longitude = np.radians(args.initial_view)

    # Inizializzazione del field of view
    fov = np.radians(args.fov)

    # Inizializzazione della initial view
    phi_rot, theta_rot = latitude, longitude

    # Inizializzazione del piano canonico iniziale
    canonic_plane = gen_Canonic_Plane(fov)

    # Inizializzazione delle variabili che conterranno il percorso del video o dell'immagine
    video, image = None, None

    # Verifica del caricamento del video o dell'immagine
    if args.video is not None:
        video = cv2.VideoCapture(args.video)
        source_type = "video"

    elif args.image is not None:
        image = cv2.imread(args.image)
        source_type = "image"

    else:
        raise IOError("video or image not found")


    # Loop principale per il video o l'immagine
    while True:
        # Lettura dell'immagine di input
        if source_type == "video":
            ret, img = video.read()
        else:
            img = image.copy()

        # Uscita dal loop se non viene caricata nessuna immagine    
        if img is None:
            break

        H_img_input, W_img_input, canali = img.shape

        # Trasformazione delle coordinate equi-rettangolari in coordinate planari
        map_x, map_y = equi_to_planar(canonic_plane, H_img_input, W_img_input)
        output_image = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)

        cv2.imshow("Output image", output_image)

        key = cv2.waitKey(1)
        handle_keyboard_input(key)
        
        # Uscita con il tasto ESC o se finisce il video
        if key == 27:
            break

    # Rilascia le risorse e chiude tutte le finestre
    if source_type == "video":
        video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str, help="Path to the video file")
    parser.add_argument("--image", type=str, help="Path to the image file")
    parser.add_argument("--initial_view", nargs=2, type=float, default=[0, 0], help="Initial initial_view as latitude and longitude in degrees (default: 0 0)")
    parser.add_argument("--fov", type=float, default=60, help="Field of view in degrees (default: 60)")
    args = parser.parse_args()

    # avvio il programma
    main(args)