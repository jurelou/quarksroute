

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

    def analyse(self, cheminFichierBrut):
        """
        Apelle la fonction _analysefile() avec le chemin donné

        retourne le chemin vers le fichier d'analyse
        """

    def visualise(self, cheminFichierAnalysé):
        """
        apelle la fonction _display() avec le chemin donné
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
        parse toutes les lignes de l'ouput sauf la première.
        génère un identifiant unique (par ex: 89DD2)
        sérialize le resultat sous le format JSON et l'écris dans le fichier /opt/probes/traceroute/log/89DD2.xml
        retourne le chemin vers le fichier (/opt/probes/traceroute/log/89DD2.xml)
        """

    def _analysefile(self, path):
        """
        Lis le fichier via le path donné puis analyse le résulat
        (par example: générer les latences moyennes, maximales, minimales pour chaque "hop")
        Ecrire le resultat dans le fichier d'analyse.
        Par example: le fichier de résultat est: /opt/probes/traceroute/log/89DD2.xml
        Le fichier d'analyse sera: /opt/probes/traceroute/log/89DD2-analyse.xml

        Retourner le chemin vers le fichier d'analyse
        """

    def _display(self, path):
        """
        Lis le fichier via le chemin donné, et  affiche le résultat
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
