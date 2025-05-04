import random
import json
import os
import datetime
import colorama
from colorama import Fore, Style
from difflib import SequenceMatcher
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Inicializar colorama para formateo de texto en consola
colorama.init()

# # Descargar recursos de NLTK necesarios (ejecutar la primera vez)
# try:
#     nltk.data.find('tokenizers/punkt')
#     nltk.data.find('corpora/stopwords')
# except LookupError:
#     nltk.download('punkt')
#     nltk.download('stopwords')

class OrgueBotMemoria:
    """Clase para gestionar la memoria del chatbot"""
    def __init__(self, ruta_archivo="memoria_orguebot.json"):
        self.ruta_archivo = ruta_archivo
        self.memoria = self._cargar_memoria()
        
    def _cargar_memoria(self):
        """Carga la memoria desde el archivo JSON o crea una nueva si no existe"""
        try:
            if os.path.exists(self.ruta_archivo):
                with open(self.ruta_archivo, 'r', encoding='utf-8') as archivo:
                    return json.load(archivo)
            else:
                return {"conversaciones": [], "preguntas_frecuentes": {}, "feedback": {}, "huevos_pascua_encontrados": []}
        except Exception as e:
            print(f"Error al cargar memoria: {e}")
            return {"conversaciones": [], "preguntas_frecuentes": {}, "feedback": {}, "huevos_pascua_encontrados": []}
    
    def guardar_memoria(self):
        """Guarda la memoria en el archivo JSON"""
        try:
            with open(self.ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(self.memoria, archivo, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar memoria: {e}")
    
    def registrar_conversacion(self, conversacion):
        """Registra una conversación completa"""
        self.memoria["conversaciones"].append({
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "intercambios": conversacion
        })
        self.guardar_memoria()
    
    def registrar_pregunta(self, pregunta, categoria):
        """Registra una pregunta frecuente y su categoría"""
        if pregunta.lower() in self.memoria["preguntas_frecuentes"]:
            self.memoria["preguntas_frecuentes"][pregunta.lower()]["frecuencia"] += 1
        else:
            self.memoria["preguntas_frecuentes"][pregunta.lower()] = {
                "categoria": categoria,
                "frecuencia": 1
            }
        self.guardar_memoria()
    
    def obtener_sugerencias(self, n=3):
        """Devuelve las n preguntas más frecuentes"""
        ordenadas = sorted(
            self.memoria["preguntas_frecuentes"].items(),
            key=lambda x: x[1]["frecuencia"],
            reverse=True
        )
        return [pregunta for pregunta, _ in ordenadas[:n]]
    
    def registrar_easter_egg(self, nombre):
        """Registra un huevo de pascua encontrado"""
        if nombre not in self.memoria["huevos_pascua_encontrados"]:
            self.memoria["huevos_pascua_encontrados"].append(nombre)
            self.guardar_memoria()
            return True
        return False

class OrgueBot:
    """Clase principal del chatbot especializado en órganos musicales"""
    def __init__(self):
        # Inicialización
        self.memoria = OrgueBotMemoria()
        self.cargar_conocimientos()
        self.conversacion_actual = []
        self.contexto_actual = None
        self.ultima_categoria = None
        self.stopwords = set(stopwords.words('spanish'))
        self.modo_divertido = False
        self.contador_preguntas = 0
        
    def cargar_conocimientos(self):
        """Carga la base de conocimientos"""
        # Base de conocimientos en español
        self.conocimientos = {
            "historia": [
                "El órgano es uno de los instrumentos más antiguos que sigue en uso. Sus orígenes se remontan al siglo III a.C. con el hydraulis griego. 🎹",
                "Los órganos de tubos modernos empezaron a aparecer en las iglesias europeas alrededor del siglo VIII. ⛪",
                "El período barroco (1600-1750) se considera la edad de oro de la música para órgano, con compositores como Bach llevando el instrumento a su máxima expresión. 🎼",
                "En el siglo XIX, los órganos se volvieron más grandes y versátiles, incorporando nuevos registros y mecanismos. 🔧",
                "El órgano Hammond fue inventado en 1935 por Laurens Hammond como una alternativa económica a los órganos de tubos para iglesias. 💰",
                "¿Sabías que el primer órgano documentado en España llegó como regalo del emperador bizantino Constantino V al rey Pipino el Breve en el año 757? 📜",
                "Durante la Revolución Francesa, muchos órganos fueron destruidos por considerarse símbolos del antiguo régimen. ¡Menos mal que no todos corrieron esa suerte! 🇫🇷",
                "El órgano más antiguo del mundo que todavía funciona está en la Basílica de Valère en Sion, Suiza, y data de alrededor de 1435. ¡Casi 600 años sonando! 🇨🇭",
            ],
            "compositores": [
                "Johann Sebastian Bach es considerado el más grande compositor para órgano. Sus obras incluyen la Toccata y Fuga en Re menor y los Preludios Corales. 👑",
                "Dietrich Buxtehude fue una gran influencia para Bach. Sus obras para órgano incluyen preludios, fugas y chaconas. 🎵",
                "César Franck revitalizó la música de órgano en Francia durante el siglo XIX con obras como sus Tres Corales. 🇫🇷",
                "Olivier Messiaen creó un lenguaje musical único para órgano en el siglo XX, con obras como 'La Nativité du Seigneur'. 🌟",
                "Felix Mendelssohn contribuyó significativamente al repertorio con sus Sonatas para órgano, ayudando a revivir el interés por Bach. 📚",
                "Charles-Marie Widor es famoso por su 'Toccata' de la Quinta Sinfonía para órgano, una pieza frecuente en bodas. 💒",
                "Louis Vierne, organista ciego de Notre-Dame de París, murió en 1937 mientras daba un recital en su amado órgano. ¡Un final dramático para un gran músico! 🎭",
                "Max Reger escribió algunas de las obras más complejas para órgano, con armonías cromáticas y estructuras contrapuntísticas densas. ¡Todo un desafío! 🧩",
                "Antonio de Cabezón, organista ciego español del siglo XVI, fue pionero en la música para teclado y una gran influencia en toda Europa. ¡Orgullo español! 🇪🇸",
                "¿Sabías que Mozart llamaba al órgano 'el rey de los instrumentos'? Aunque no compuso mucho para él, lo admiraba enormemente. 👑",
            ],
            "estructura": [
                "Un órgano de tubos consta principalmente de tubos, consolas con teclados y pedales, y un sistema para suministrar aire a los tubos. 🎛️",
                "Los teclados manuales del órgano se llaman 'manuales', y un órgano puede tener desde uno hasta siete de ellos. 🎹",
                "El pedalero es un teclado tocado con los pies, generalmente con 30-32 teclas, y controla los sonidos más graves. 👣",
                "Los registros son conjuntos de tubos con un timbre particular. Pueden simular diferentes instrumentos o crear sonidos únicos del órgano. 🎺",
                "Los tubos pueden ser labiales (como una flauta) o de lengüeta (con una vibración de caña), creando diferentes timbres. 🎵",
                "El 'secreto' es la cámara de aire presurizado que distribuye el viento a los tubos cuando se presionan las teclas. ¡Es el corazón del órgano! 💨",
                "La tracción es el sistema que conecta las teclas con las válvulas que permiten el paso del aire a los tubos. Puede ser mecánica, neumática, eléctrica o combinada. ⚡",
                "Algunos órganos gigantes tienen tubos tan grandes que podrían caber una persona dentro. El más grande puede medir hasta 19 metros de altura. ¡Imagina el sonido! 📏",
                "Los tubos de órgano se fabrican principalmente con aleaciones de estaño y plomo, aunque también pueden ser de madera, cobre o incluso bambú. 🪵",
                "Los 'tiradores' o 'registros' son los controles que el organista utiliza para seleccionar qué juegos de tubos sonarán. Un órgano grande puede tener más de 100. 🎚️",
            ],
            "tecnica": [
                "La técnica del órgano difiere del piano: no hay dinámica por presión, se debe controlar la articulación y usar registros para variar la intensidad. 🎯",
                "El 'toque legato' es fundamental en la interpretación del órgano, especialmente en música romántica y moderna. ✨",
                "La registración es el arte de seleccionar y combinar los diferentes registros para lograr el color tonal deseado. 🎨",
                "La técnica de pedaleo requiere años de práctica para dominar movimientos como el 'talón-punta' y cruces de pies. 🦶",
                "La improvisación ha sido históricamente una habilidad esencial para los organistas, especialmente en contextos litúrgicos. 🎶",
                "Un buen organista debe poder leer tres pentagramas simultáneamente: dos para las manos y uno para los pies. ¡Todo un desafío de coordinación! 👀",
                "El 'appoggiatura' es un adorno muy utilizado en la música barroca para órgano que consiste en una nota rápida antes de la nota principal. 🎭",
                "La técnica de 'staccato' en órgano es más compleja que en piano, pues depende no solo de cómo se toca la tecla sino también de la acústica del espacio. 🏛️",
                "En la interpretación de Bach, se debate entre un toque más articulado (al estilo barroco) o más legato (como en la tradición romántica). ¿Tú cuál prefieres? 🤔",
                "La técnica de pedaleo 'talón-punta' fue desarrollada en el siglo XIX y permite mayor agilidad con los pies que las técnicas antiguas. 💃",
            ],
            "organos_famosos": [
                "El órgano Cavaillé-Coll de Saint-Sulpice en París es uno de los instrumentos más grandes y prestigiosos del mundo. 🇫🇷",
                "El órgano de la Catedral de Notre-Dame en París es históricamente significativo y ha sido tocado por grandes músicos como Louis Vierne. 🔔",
                "El órgano Wanamaker en Filadelfia es el órgano de tubos funcional más grande del mundo, con más de 28,000 tubos. 🇺🇸",
                "El órgano Silbermann de la Iglesia de Santo Tomás en Leipzig es famoso por su asociación con J.S. Bach. 🇩🇪",
                "El órgano de la Mezquita-Catedral de Córdoba es uno de los más importantes de España, construido por el famoso organero José Martínez Colmenero. 🇪🇸",
                "El órgano del Royal Albert Hall de Londres, apodado 'La Voz de Júpiter', es uno de los más grandes del mundo con 9,999 tubos. ¿Por qué no 10,000? ¡Dicen que fue para evitar impuestos adicionales! 💷",
                "El órgano de bambú de Las Piñas, Filipinas, es único en el mundo porque sus tubos están hechos de bambú en lugar de metal. ¡Sonido exótico garantizado! 🎍",
                "El órgano de la Basílica de Mafra en Portugal tiene seis órganos que pueden tocarse simultáneamente. ¡Menudo espectáculo sonoro! 🇵🇹",
                "El llamado 'órgano de estalactitas' en Virginia, EE.UU., no es un órgano tradicional sino una formación rocosa que suena al ser golpeada. ¡La naturaleza también crea instrumentos! 🗿",
                "El órgano de la Sydney Opera House en Australia tiene 10,154 tubos y su construcción tardó 10 años. ¡Vale la pena escucharlo si visitas el país! 🦘",
            ],
            "musica_liturgica": [
                "El órgano ha sido el instrumento principal en la música litúrgica cristiana durante siglos. ⛪",
                "En la tradición católica, el órgano acompaña cantos, proporciona música para momentos de reflexión y marca momentos importantes de la liturgia. 🙏",
                "En las iglesias protestantes, especialmente luteranas, el órgano acompaña himnos congregacionales y corales. 📖",
                "El año litúrgico (Adviento, Navidad, Cuaresma, Pascua, etc.) tiene música específica para órgano asociada a cada temporada. 📅",
                "Muchos compositores han escrito colecciones de piezas para cubrir las necesidades del año litúrgico, como el 'Orgelbüchlein' de Bach. 📚",
                "Durante el Concilio Vaticano II (1962-1965) se discutió el papel del órgano en la liturgia, reafirmando su importancia pero abriendo la puerta a otros instrumentos. 🎸",
                "El canto gregoriano a menudo se alterna con versos de órgano en lo que se llama 'alternatim practice', una tradición que se remonta al siglo XV. 📜",
                "El Improperium es una forma específica de improvisación organística durante la liturgia del Viernes Santo. ✝️",
                "En algunas tradiciones, el órgano guarda silencio durante la Cuaresma para regresar gloriosamente en la Vigilia Pascual. 🌅",
                "Los 'versos de órgano' son piezas cortas que sustituyen versos cantados del Magnificat o de los salmos en la liturgia. 🎵",
            ],
            "mantenimiento": [
                "Los órganos de tubos requieren afinación regular, especialmente cuando cambian las temperaturas estacionales. 🔧",
                "La humedad es un factor crítico para los órganos de tubos: muy poca puede agrietar la madera, demasiada puede causar oxidación. 💧",
                "Los órganos históricos a menudo mantienen su entonación original, que puede ser diferente del estándar moderno A=440Hz. 🎵",
                "El mantenimiento preventivo incluye limpieza de polvo, ajuste de mecanismos y revisión de fugas de aire. 🧹",
                "La restauración de órganos históricos es una especialidad que combina conocimientos de música, historia, artesanía y conservación. 🏺",
                "Los fuelles de un órgano antiguo solían requerir personas que los accionaran manualmente durante todo el concierto o servicio. ¡Un trabajo agotador! 💪",
                "La polilla puede ser un enemigo mortal para los órganos con piezas de madera. ¡Algunos organeros utilizan tratamientos especiales para protegerlos! 🦋",
                "Cada tubo debe ser afinado individualmente, lo que significa que un órgano grande puede requerir varios días para una afinación completa. ⏱️",
                "El temperamento igual, usado en pianos modernos, no siempre se aplica en órganos históricos que pueden usar temperamentos mesotónicos u otros sistemas de afinación. 🧮",
                "El polvo es uno de los mayores enemigos del órgano, ya que puede entrar en los tubos y cambiar su sonido. Algunos órganos modernos incorporan filtros de aire. 🌬️",
            ],
            "curiosidades": [
                "El órgano más pesado del mundo es el de la Catedral de Liverpool, con más de 32,000 tubos y un peso de unas 250 toneladas. ¡Como 40 elefantes! 🐘",
                "La nota más grave de un órgano puede ser tan baja que no se oye sino que se siente como una vibración. ¡Literalmente te sacude! 📳",
                "En la Edad Media, algunos órganos tenían teclas tan grandes que debían ser golpeadas con los puños o los codos. ¡No era un instrumento para delicados! 👊",
                "El órgano de agua romano (hydraulis) usaba agua para regular la presión del aire. ¡Una ingeniería avanzada para la época! 💦",
                "Algunos órganos históricos contienen metales preciosos como el oro y la plata en sus tubos para obtener timbres específicos. 💎",
                "El 'Hallelujah Chorus' de Händel a menudo se toca con órgano, aunque originalmente fue compuesto para orquesta y coro. 🎭",
                "En algunos países, los organistas tienen que aprobar exámenes oficiales para poder tocar en iglesias importantes. ¡Nada de aficionados! 📝",
                "En la época barroca, el organista a menudo también dirigía el coro y la orquesta desde el órgano. ¡Un verdadero multitasking! 🧠",
                "El aire que entra en los tubos del órgano debe ser perfectamente limpio. Incluso una partícula pequeña puede cambiar el sonido de un tubo. 🌬️",
                "Algunos tubos de órgano están hechos de madera y pueden tener forma cuadrada en lugar de cilíndrica. ¡La forma afecta al sonido! 📦",
            ]
        }
        
        # Mensajes del sistema
        self.mensajes = {
            "saludos": [
                "¡Bienvenido al Chatbot del Órgano! ¿En qué puedo ayudarte hoy? 🎹",
                "¡Hola! Soy el asistente virtual especializado en órganos musicales. ¿Qué te gustaría saber? 🎵",
                "Bienvenido al mundo del órgano. ¿Tienes alguna pregunta sobre este magnífico instrumento? 🎼",
                "¡Saludos! Estoy aquí para compartir conocimientos sobre el órgano y su música. ¿Qué te interesa saber? 🎶",
                "¡Hola organófilo! ¿Listo para explorar el fascinante mundo de los órganos musicales? 🎭"
            ],
            "despedidas": [
                "¡Gracias por conversar sobre órganos! Espero haberte ayudado. ¡Hasta pronto! 👋",
                "Ha sido un placer compartir información sobre este maravilloso instrumento. ¡Vuelve pronto! 🎵",
                "Espero que hayas aprendido algo nuevo sobre el órgano hoy. ¡Hasta la próxima! 📚",
                "¡Adiós! Si tienes más preguntas sobre el órgano, no dudes en volver a consultarme. 🎹",
                "¡Que tus días estén llenos de música! ¡Hasta pronto! 🎶"
            ],
            "no_info": [
                "Lo siento, no tengo información específica sobre eso. ¿Hay algo más sobre órganos que te gustaría saber? 🤔",
                "Esa es una pregunta interesante, pero no tengo datos precisos al respecto. ¿Puedo ayudarte con otro aspecto del órgano? 📝",
                "No dispongo de esa información en mi base de conocimientos. ¿Te interesa saber sobre la historia, compositores o técnica del órgano? 📚",
                "No tengo detalles sobre eso, pero puedo informarte sobre la estructura del órgano, compositores famosos o técnicas de interpretación. 🧐",
                "Mmm... esa pregunta se sale de mi registro. ¿Quieres probar con otra? 🎵"
            ],
            "sugerencias": "Si no sabes qué preguntar, estas son algunas preguntas populares:",
            "ayuda": "Puedes preguntarme sobre historia, compositores, estructura, técnica, órganos famosos, música litúrgica, mantenimiento u otras curiosidades del órgano. También puedo contarte algún dato curioso aleatorio si escribes 'dato curioso'.",
            "modo_divertido_on": "¡Modo divertido activado! 🎭 Prepárate para respuestas con más ritmo y melodía.",
            "modo_divertido_off": "Modo divertido desactivado. Volvemos a la seriedad del órgano. 🎹",
            "datos_curiosos": [
                "¿Sabías que el órgano de la Catedral de Passau en Alemania tiene 17,974 tubos y 233 registros? ¡Es uno de los órganos de iglesia más grandes del mundo! 🏆",
                "En la antigüedad, se necesitaban hasta 12 personas para accionar los fuelles de un órgano grande. ¡Todo un equipo de 'sopladores'! 💨",
                "El organista Johann Ludwig Krebs fue alumno de Bach. Su apellido significa 'cangrejo' en alemán, y Bach bromeaba: '¡Es el único cangrejo en mi arroyo!' 🦀",
                "Algunos órganos tienen tubos hechos de madera de más de 500 años de antigüedad que siguen funcionando perfectamente. ¡Una longevidad impresionante! 🌳",
                "¿Te imaginas tocar 7 teclados a la vez? El órgano Atlantic City Convention Hall tiene ese número de manuales. ¡Necesitarías ser un pulpo! 🐙",
                "Mozart escribió música para un instrumento llamado 'Orgelwalze', un tipo de órgano mecánico similar a una caja de música. 🎡",
                "El órgano de la abadía de Weingarten en Alemania tiene una fachada tan espectacular que se le conoce como 'el órgano Gabler' en honor a su constructor. ¡Un verdadero tesoro barroco! 🏛️",
                "El dióxido de carbono exhalado por la congregación en una iglesia puede desafinar los tubos del órgano con el tiempo. ¡Respirar afecta a la música! 😮"
            ]
        }

        # Easter eggs
        self.easter_eggs = {
            "konami": {
                "clave": "arriba arriba abajo abajo izquierda derecha izquierda derecha b a",
                "respuesta": "🎮 ¡CÓDIGO KONAMI ACTIVADO! Acabas de desbloquear el modo organista invencible. Ahora puedes tocar Bach a 200 BPM sin equivocarte. ¡Poderes ilimitados! 🎹🔥",
                "nombre": "konami_code"
            },
            "star_wars": {
                "clave": "que la fuerza te acompañe",
                "respuesta": "🎵 *Suena el tema de Star Wars en el órgano* 🚀 El Maestro Yoda dice: 'Tocar el órgano debes, mmm sí. El camino al lado luminoso de la música es.'",
                "nombre": "jedi_organista"
            },
            "toccata": {
                "clave": "toccata y fuga",
                "respuesta": "🧛‍♂️ *Relámpagos y truenos* ¡Muahaha! Has invocado al Fantasma de la Ópera y al Conde Drácula simultáneamente. Ambos te piden autógrafos por tu exquisito gusto musical. La Toccata y Fuga en Re menor de Bach es su melodía favorita para hacer entradas dramáticas.",
                "nombre": "phantom_dracula"
            },
            "rickroll": {
                "clave": "never gonna give you up",
                "respuesta": "🎵 *El órgano comienza a tocar 'Never Gonna Give You Up'* ¡Has sido ORGANROLLADO! Rick Astley estaría orgulloso de esta versión para órgano de su clásico. 🎹🕺",
                "nombre": "organroll"
            },
            "bach_secret": {
                "clave": "b a c h",
                "respuesta": "🎼 *El órgano toca la secuencia de notas Si♭-La-Do-Si♮* ¡Has descubierto el motivo BACH! En notación alemana, estas notas deletrean B-A-C-H. El propio Johann Sebastian usó este motivo en sus composiciones. ¡Eres un verdadero conocedor! 👏",
                "nombre": "motivo_bach"
            }
        }
        
        self.categorias_palabras = {
            "historia": ["historia", "origen", "antiguo", "evolución", "histórico", "cuando", "comenzó", "inventó", "creó", "surgió"],
            "compositores": ["compositor", "bach", "buxtehude", "franck", "messiaen", "mendelssohn", "músico", "autor", "escribió", "compuso"],
            "estructura": ["estructura", "parte", "tubo", "consola", "manual", "pedal", "registro", "construcción", "diseño", "componente"],
            "tecnica": ["técnica", "tocar", "interpretar", "ejecución", "pedal", "digitación", "registración", "método", "práctica", "estudio"],
            "organos_famosos": ["famoso", "importante", "grande", "catedral", "iglesia", "notre dame", "wanamaker", "conocido", "monumental", "impresionante"],
            "musica_liturgica": ["liturgia", "misa", "iglesia", "religioso", "servicio", "culto", "ceremonia", "ritual", "sagrado", "eclesiástico"],
            "mantenimiento": ["mantener", "afinar", "restaurar", "conservar", "reparar", "cuidar", "preservar", "ajustar", "limpiar", "renovar"],
            "curiosidades": ["curioso", "interesante", "insólito", "extraño", "sorprendente", "dato", "sabías", "impactante", "anécdota", "fascinante"]
        }
    
    def _preprocesar_texto(self, texto):
        """Preprocesa el texto para análisis"""
        # Tokenización y filtrado de stopwords
        tokens = word_tokenize(texto.lower())
        return [token for token in tokens if token not in self.stopwords]
    
    def _calcular_similitud(self, texto1, texto2):
        """Calcula la similitud entre dos textos"""
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()

    def categorizar_pregunta(self, pregunta):
        """Determina la categoría de la pregunta utilizando NLP"""
        pregunta_procesada = ' '.join(self._preprocesar_texto(pregunta))
        
        # Si hay contexto previo, dar preferencia a la misma categoría
        if self.ultima_categoria:
            puntuacion_contexto = 0.2  # Bonus por mantener contexto
        else:
            puntuacion_contexto = 0
        
        mejor_categoria = None
        mejor_puntuacion = 0.3  # Umbral mínimo de confianza
        
        # Evaluar cada categoría
        for categoria, palabras_clave in self.categorias_palabras.items():
            puntuacion = puntuacion_contexto if categoria == self.ultima_categoria else 0
            
            # Comprobar coincidencia con palabras clave
            for palabra in palabras_clave:
                if palabra in pregunta_procesada:
                    puntuacion += 0.15
            
            # Evaluar la pregunta completa contra cada palabra clave
            for palabra in palabras_clave:
                similitud = self._calcular_similitud(pregunta_procesada, palabra)
                puntuacion += similitud * 0.1
            
            if puntuacion > mejor_puntuacion:
                mejor_categoria = categoria
                mejor_puntuacion = puntuacion
        
        # Actualizar contexto
        self.ultima_categoria = mejor_categoria
        return mejor_categoria
    
    def verificar_easter_eggs(self, mensaje):
        """Verifica si el mensaje activa algún easter egg"""
        mensaje_lower = mensaje.lower().strip()
        
        for nombre, egg in self.easter_eggs.items():
            if egg["clave"] in mensaje_lower:
                encontrado_nuevo = self.memoria.registrar_easter_egg(egg["nombre"])
                if encontrado_nuevo:
                    return f"{egg['respuesta']} 🎉 ¡Has encontrado un nuevo easter egg!"
                return egg["respuesta"]
        
        # Easter egg secreto del modo divertido
        if mensaje_lower == "modo divertido":
            self.modo_divertido = not self.modo_divertido
            return self.mensajes["modo_divertido_on"] if self.modo_divertido else self.mensajes["modo_divertido_off"]
        
        # Easter egg para datos curiosos
        if mensaje_lower in ["dato curioso", "datos curiosos", "curiosidad", "cuéntame algo interesante"]:
            return random.choice(self.mensajes["datos_curiosos"])
        
        return None

    def responder_pregunta(self, pregunta):
        """Responde la pregunta del usuario"""
        # Verificar primero si es un easter egg
        respuesta_egg = self.verificar_easter_eggs(pregunta)
        if respuesta_egg:
            return respuesta_egg
        
        # Incrementar contador de preguntas
        self.contador_preguntas += 1
        
        # Easter egg secreto: cada 10 preguntas da un dato curioso
        if self.contador_preguntas % 10 == 0:
            return f"¡Pregunta número {self.contador_preguntas}! Para celebrarlo, aquí tienes un dato curioso: {random.choice(self.mensajes['datos_curiosos'])}"
        
        # Determinar categoría
        categoria = self.categorizar_pregunta(pregunta)
        
        # Registrar pregunta si se identificó una categoría
        if categoria:
            self.memoria.registrar_pregunta(pregunta, categoria)
            respuesta_base = random.choice(self.conocimientos[categoria])
            
            # Si está en modo divertido, añadir más emojis y entusiasmo
            if self.modo_divertido:
                emojis = "🎵🎹🎭🎼🎶🎧🎻"
                respuesta_base = respuesta_base.replace(".", "! 🎵").replace(",", ", ¡vaya! ")
                return f"{respuesta_base} {random.choice(emojis)}{random.choice(emojis)}"
            return respuesta_base
        else:
            return random.choice(self.mensajes["no_info"])

    def es_despedida(self, mensaje):
        """Verifica si el mensaje es una despedida"""
        mensaje = mensaje.lower()
        palabras_despedida = ["adiós", "chao", "hasta luego", "salir", "terminar", "cerrar", "bye", "me voy", "hasta pronto"]
        
        return any(palabra in mensaje for palabra in palabras_despedida)
    
    def es_ayuda(self, mensaje):
        """Verifica si el usuario pide ayuda"""
        mensaje = mensaje.lower()
        return "ayuda" in mensaje or "help" in mensaje or "?" == mensaje
    
    def mostrar_sugerencias(self):
        """Muestra sugerencias de preguntas al usuario"""
        sugerencias_memoria = self.memoria.obtener_sugerencias()
        
        if sugerencias_memoria:
            print(f"\n{Fore.CYAN}{self.mensajes['sugerencias']}{Style.RESET_ALL}")
            for i, sugerencia in enumerate(sugerencias_memoria, 1):
                print(f"{Fore.CYAN}{i}. {sugerencia}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.CYAN}{self.mensajes['ayuda']}{Style.RESET_ALL}")
    
    def iniciar(self):
        """Inicia el chatbot"""
        print(f"{Fore.GREEN}{random.choice(self.mensajes['saludos'])}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Escribe 'ayuda' en cualquier momento para ver opciones.{Style.RESET_ALL}")
        self.conversacion_actual = []
        
        while True:
            # Mostrar sugerencias cada 5 intercambios
            if len(self.conversacion_actual) % 5 == 0 and self.conversacion_actual:
                self.mostrar_sugerencias()
            
            # Obtener input del usuario
            mensaje_usuario = input(f"{Fore.YELLOW}Tú: {Style.RESET_ALL}")
            
            # Registrar la pregunta
            self.conversacion_actual.append({"rol": "usuario", "mensaje": mensaje_usuario})
            
            # Verificar si el usuario quiere salir
            if self.es_despedida(mensaje_usuario):
                respuesta = random.choice(self.mensajes["despedidas"])
                print(f"{Fore.GREEN}Bot: {respuesta}{Style.RESET_ALL}")
                self.conversacion_actual.append({"rol": "bot", "mensaje": respuesta})
                self.memoria.registrar_conversacion(self.conversacion_actual)
                break
            
            # Verificar si pide ayuda
            if self.es_ayuda(mensaje_usuario):
                print(f"{Fore.GREEN}Bot: {self.mensajes['ayuda']}{Style.RESET_ALL}")
                self.conversacion_actual.append({"rol": "bot", "mensaje": self.mensajes["ayuda"]})
                continue
                
            # Responder la pregunta
            respuesta = self.responder_pregunta(mensaje_usuario)
            print(f"{Fore.GREEN}Bot: {respuesta}{Style.RESET_ALL}")
            self.conversacion_actual.append({"rol": "bot", "mensaje": respuesta})

# Ejecutar el chatbot
if __name__ == "__main__":
    try:
        chatbot = OrgueBot()
        chatbot.iniciar()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Programa interrumpido por el usuario.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error inesperado: {e}{Style.RESET_ALL}")
