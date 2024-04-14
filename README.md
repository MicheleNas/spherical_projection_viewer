--------------------------------- START --------------------------------- 
Opzioni: --video, --image, --initial_view, --fov

Avvio:
- Esecuzione video: python file_name.py --video video_name
- Esecuzione immagine : python file_name.py --image image_name

- Per settare la vista inziale e la fov: python file_name.py --video video_name --initial_view val_lat val_lon --fov degrees

Comandi dopo l'avvio:
- A: per muoversi verso sx
- D: per muoversi verso dx
- W: per muoversi verso l'alto
- S: per muoversi verso il basso

- +: per zoom di avvicinamento, che ingrandirà l'immagine.
- -: per zoom di distanziamento, che rimpicciolirà l'immagine.

- Esc: termina l'esecuzione del video

--------------------------------- REPORT --------------------------------- 

La relazione qui di seguito descrive l'algoritmo implementato per la trasformazione di un video a proiezione equirettangolare in vista prospettica planare, consentendo al contempo l'iterazione dell'utente tramite input da tastiera per regolare gli angoli di rotazione in tempo reale. L'algoritmo è stato sviluppato utilizzando Python e le librerie : opencv e numpy.

All'inizio del codice vengono definite come variabili globali gli angoli di rotazione phi_rot e theta_rot, che permettono di ruotare l'immagine dato l'input da tastiera (A: sx, D: dx, W: up, S: down).
Viene definita un ulteriore variabile globale 'zoom_factor' che permetterà di mettere a fuoco le parti dell'immagine, utilizzando i tasti (+: zoom avanti, -: zoom indietro)

Le funzioni principali che permettono l'esecuzione dell'algoritmo sono:

1. gen_canonic_plane(): 
genera il piano canonico tangente alla sfera considerando come punto del piano tangente p = (1,0,0), e considerando anche un field of view iniziale.
Nello specifico genera una griglia di punti, appartenenti ad uno spazio 3D, che rappresentano la PROIEZIONE di una porzione della sfera tangente al piano. La griglia è rappresentata da un array multidimensionale di dimensione (H, W, 3) [dove H e W rappresentano le dimensioni dell'immagine]

All'interno di questa funzione vengono definite le dimensioni dell'immagine (H, W) e gli angoli del cono di visuale (a_w e a_h). Per quanto riguarda le dimensioni dell'immagine planare è stato definito il rispettivo aspect ratio come il rapporto W/H = 16/9 (sono state testate H=500,H=1080,H=256 con successo). Per gli angoli del cono di visuale è stato impostato di default a_w = 60° (è possibile modificare questo valore direttamente da terminale mediante l'opzione --fov) in maniera tale che sia minore di 90°, mentre per l'angolo a_h è stata implementata la seguente espressione:

a_h = 2*arctan((H/W)*tan(a_w/2)) data dalla relazione trigonometrica [W/2f = tan(a_w/2) => f = W/2*tan(a_w/2)] sostituita alla formula dell'angolo di visuale verticale a_h = 2*arctan(H/2f)

2. equi_to_planar():
permette di trasformare un sistema di coordinate equirettangolari in un sistema di coordinate planari, permettendo anche l'applicazione della rotazione sferica e dello zoom digitale dell'immagine.
Per farlo tiene in considerazione come piano di partenza il piano canonico e applica a questo, qualora fosse richiesto, una rotazione o uno zoom digitale.

	- Zoom digitale: Viene effettuato trasformando i punti dell'immagine mediande la matrice 'S'.
	- Rotazione: Inizialmente la rotazione è settata di default a (0°,0°), e tramite essa è possibile settare l'initial view grazie all'opzione da terminale --initial_view val_latitudine val_longitudine. La rotazione degli assi viene applicata trasformando i punti dell'immagine mediante una matrice di rotazione 'R' ottenuta dagli angoli in input'phi_rot' e 'theta_rot' [R = Rz(phi_rot) * Ry(theta_rot)], gli assi di rotazione di interesse sono gli assi y con la rotazione laterale o pitch, e l'asse z con la rotazione yaw, attorno all'asse perpendicolare. 
	
A seguire viene effettuata la normalizzazione in modo da ottenere le coordinate dei punti della sfera che dovranno essere proiettati nell' immagine di output. Successivamente, ottenute le coordinate cartesiane dei punti della sfera vengono calcolate le coordinate polari phi e theta.

Nello specifico 'equi_to_planar()' restituisce le matrici map_x e map_y, che conterranno le coordinate dei valori dei pixel da rimappare utilizzando la tecnica dell'inverse mapping

3. 'handle_keyboard_input()':
La funzione gestisce gli input da tastiera per modificare gli angoli di rotazione phi_rot, theta_rot e lo zoom_factor. 


main:
- Inizializzazione dell'initial view e della field of view

- Inizializzazione di un piano canonico tangente ad una sfera di raggio=1, in modo da generare un piano di coordinate di base su cui lavorare.

- Mediante l'uso della funzione 'equi_to_planar()' verranno applicate una serie di trasformazioni geometriche che ruoteranno il piano mantenendolo tangente alla sfera, e effettueranno lo zoom digitale dell'immagine. Dopo aver fissato il piano nello spazio verranno applicate delle trasformazioni per calcolare le coordinate dell'immagine sorgente (equirettangolare) che dovranno essere mappate al piano canonico.

- Utilizzo di 'cv2.remap()' che applica una mappatura di trasformazione definita dalle coordinate map_x e map_y all'immagine di input. Questo metodo risulta utile in quanto semplifica l'applicazione della trasformazione senza richiedere di gestire manualmente l'interpolazione dei pixel, poiché la funzione stessa implementa l'interpolazione dei pixel utilizzando le coordinate mappate.

- Gestione dell'input da tastiera mediante 'cv2.waitKey()' e 'handle_keyboard_input()'

- Gestione dell'uscita dal loop mediante il tasto 'ESC' o qualora si stesse eseguendo un video l'uscita avverrebbe anche alla fine dell'esecuzione.


Il codice è stato testato anche su immagini, poichè è stato generalizzato per renderlo in grado di accettare in input video o immagini.
