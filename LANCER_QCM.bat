@echo off
echo ========================================================
echo      MISE A JOUR DU QCM EN COURS...
echo      (Ne fermez pas cette fenetre)
echo ========================================================

:: 1. Sauvegarde les modifications locales de l'utilisateur (JSON corrigés, Stats)
git stash

:: 2. Récupère tes mises à jour de code depuis GitHub
git pull

:: 3. Ré-applique les modifications de l'utilisateur par dessus ton code
git stash pop

:: Si "git stash pop" dit qu'il n'y avait rien à restaurer, ce n'est pas grave.
:: On efface les messages d'erreur potentiels pour ne pas effrayer l'utilisateur.
cls

echo ========================================================
echo      LANCEMENT DU QCM
echo ========================================================

:: Lance le programme Python
python QCM.py

pause