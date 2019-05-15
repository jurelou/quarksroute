
class TraceroutePlugin(PluginInterface):
    def __init__(self, options = None):
        """
        l'argument `options` est une liste de strings qui correspondent aux options par défaut lors de l'appel à traceroute
        Par example: options = ("--debug", 
                                "--interface", "ens4",
                                "--port", "42")
        NOTE: ce paramètre est facultatif, on peut prévoir une liste de paramètres par défaut.
        """

    # =====================
    #  Méthodes publiques
    # =====================

    def run(self, target, options=None):
        """
        Requiert un argument `target` qui correspond à l'hote que nous souhaitons tracer
        Il est possible d'override les options via l'argument `options`, sinon les options par défaut seront utilisées

        Lance la commande traceroute avec le host et les options.
        appeler la fonction _parseTraceroute() avec l'output de la fonction traceroute

        Retourne le chemin vers le fichier XML de resultats
        
        NOTE: on peut prévoir une liste de targets et retourner une liste de chemins
        """

    def analyse(self, cheminFichier):
        """
        apelle la fonction _unserialise avec le paramètre `cheminFichier`.
        on récupère un objet python, on y rajoute nos analyses
        (par example: générer les latences moyennes, maximales, minimales pour chaque "hop")
        apelle la fonction _serialise avec le nouvel objet python et le chemin vers le fichier d'analyse.
        Par example: le paramètre `cheminFichier` est: /opt/probes/traceroute/log/89DD2.xml
        Le fichier d'analyse sera: /opt/probes/traceroute/log/89DD2-analyse.xml

        Retourner le chemin vers le fichier d'analyse
        """

    def visualise(self, cheminFichier):
        """
        apelle la fonction _unserialise avec le paramètre `cheminFichier`
        générer les interfaces avec le résultat de la fonction _unserialise puis afficher les resultats graphiquement
        """

    def getVersion(self):
        """
        retourne la version du plugin 
        """

    # =====================
    #  Méthodes privées
    # =====================

    def _parseTraceroute(self, output):
        """
        parse toutes les lignes de l'ouput sauf la première et stocke le résultat dans un objet python
        génère un identifiant unique (par ex: 89DD2)
        crée le fichier /opt/probes/traceroute/89DD2.xml
        apelle la methode _serialize avec l'objet python et le chemin vers le fichier (/opt/probes/traceroute/89DD2.xml)

        retourne le chemin vers le fichier (/opt/probes/traceroute/log/89DD2.xml)
        """

    def _unserialise(path):
        """
        ouvre le fichier correspondant au path
        parse le fichier XML puis génère un objet python.
       
        Retourne l'objet python
       """
        
    def _serialise(path, objet):
        """
        ouvre le fichier correspondant au path
        transforme le paramètre `objet` en XML puis l'écris dans le fichier
        """
       

# =====================
#  Exemple d utilisation du plugin
# =====================

def main():
    options = ("--port", "42")
    traceroute = TraceroutePlugin(options)

    résultat = traceroute.run("google.fr")
    analyse = traceroute.analyse(résultat)
    traceroute.visualise(analyse) 
