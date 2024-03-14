# Web aplikácia pre detekciu cukrovky
Táto aplikácia slúži na nie úplne presnú detekciu cukrovky, F1 okolo 80%, ale snáď poslúži ako zadanie.
V docker-compose.yml sú definované 3 služby:
- flask_app - web aplikácia pomocou flasku na detekciu cukrovky a zápisu do databázy
- db - PostgreSQL databáza použivateľov
- admin - webové rozhranie pgAdmin pre správu databázy

## Spustenie:
pomocou skriptu start-app.sh -> cez docker-compose sa spustia všetky kontajnery

### Prístup na web aplikáciu:
http://localhost:4000  

### Prístup do pgAdmin:
http://localhost:8080
- email: db@db.sk
- password: db

### nastavenie pripojenia do databázy:
- Hostname: db
- Port: 5432
- Maintance database: db
- Username: db
- Password: db

**jednoduchý príkaz zobrazenia, tých, ktorí vyplnili formulár:**
`SELECT * FROM user_data;`

## Vypnutie
 tento skript zastaví všetky kontajnery: end-app.sh
 
## Odstránenie
 pomocou skriptu remove-app.sh sa odstránia všetky kontajnery, images a volumes.