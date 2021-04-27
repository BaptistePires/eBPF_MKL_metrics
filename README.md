# Benchmark eBPF vs Linux Module
## Dépendances
Ce programme a été testé sur un noyau linux 5.10.17.  
Pour son bon fonctionnement, il faut :  
- Compiler le noyau avec les flags suivant : TODO
- Avoir `python 3.x` d'installé ainsi que les librairies suivantes : `numpy`, 
`seaborn`, `pandas`, matplotlib`.
- Pour que le programme puisse s'exécuter, il a besoin des privilèges de `super-utilisateur`.
## Configuration
Dans un premier temps il faut configurer le programme.  
Vous pouvez générer un fichier de configuration vierge avec la la commande `sudo python main.py -c`. 
Un fichier nommé `config.json` sera généré.  

Si vous compilez les programmes sur une machine et les exécutez sur une autre via un dossier partager, il faudra mettre des chemin relatif au dossier où se trouve le programme du banc de test.  

Vous devrez renseigner différentes informations :  
- `bpf` Contiendra les données du programme  `eBPF` à tester.
    - `dir`: Dossier où se trouve le programme.
    - `bpf_filename`: Nom de votre fichier `eBPF` (`foo` ou `foo.o`) (changer le nom de cet attr)
- `module` Contient toutes les données du module équivalent à votre programme `eBPF`.
    - `dir` : Comme `bpf` mais pour votre module.
    - `name` : Nom du fichier contenant le module (`foo.ko`)
    - `kobj_name` : Nom ou chemin (ne pas renseigner `/sys/kernel`) du `kobject` où votre module va écrire ses mesures de temps (`foo` ou `foo/bar`)
- `tester` : Script shell qui sera exécuter pour générer les événements pour déclencher vos programmes `eBPF` et votre module. Par exemple l'insertion (et le retrait) d'un module qui fait des appels à `printk`.  
## Utilisation
Pour le moment, deux modes sont supportés :  
- La mesure des temps chargements dans le kernel. Pour utiliser cette fonctionnalité : `sudo python main.py <--loading ou -l>`

Pour les programmes `eBPF`, les fonctions `bpf_check` et `bpf_int_jit_compile` sont mesurées via le `sysfs` ainsi que le temps total d'insertion.  
Pour les modules, à l'heure actuelle, seulement le temps total d'insertion est mesuré.  
A la fin de l'exécution, deux fichiers seront dans le dossier `out` où se trouveront les données récupérées.  
- La mesure de l'overhead à chaque appel. Pour utiliser cette fonctionnalité : `sudo python main.py <--execution ou -e>`
Cela va, à tour de rôle, insérer le programme `eBPF` et le module et à chaque fois faire appel à votre script `tester` qui est censé déclencher les évennements.  

Pour chacun des programmes, les données de temps seront récupérées et des figures seront générées, vous pouvez les trouver dans le dossier `out`. Les données seront également sauvegardées dans ce dossier.
