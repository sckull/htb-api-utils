# htb-api-utils

Small script for interaction with HackTheBox API.

- Shows information of any of the current 368 machines.
- Lists all the current active and retired machines.
- Creates a small card for any Machine in HTB using the template file `card.template` for the hugo theme [zzo](https://github.com/zzossig/hugo-theme-zzo).

## Usage
```bash
 π htb-api-utils main ❯ export HTB_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvZSBNYW1hIiwiaWF0IjoxNTE2MjM5MDIyfQ.76bhkUrG-R_Ku7q0TQTobSDJbtwgAUGf-MX8GAY_kRs
 π htb-api-utils main ❯ ./hackthebox.py --help
Usage: hackthebox.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  card          Gets card info of the Machine by Name using template card
  info          Gets info of the Machine by Name
  list_active   Lists all the current Active Machines
  list_all      Lists all Machines.
  list_retired  Lists all retired Machines
 π htb-api-utils main ❯ ./hackthebox.py info Arkham
+------------+----------------------------------------+
| Info       | HackTheBox                             |
+------------+----------------------------------------+
| Name       | Arkham                                 |
| OS         | Windows                                |
| IP         | 10.10.10.130                           |
| Release    | 2019-03-16                             |
| Difficulty | Medium                                 |
| Points     | 0                                      |
| Completed? | Yes                                    |
| Active?    | Nope!                                  |
| User Owns  | 1839                                   |
| Root Owns  | 1721                                   |
| Maker      | MinatoTW                               |
| User Blood | User Blood by snowscan in 0H 55M 34S   |
| User Root  | System Blood by snowscan in 2H 44M 27S |
+------------+----------------------------------------+
 π htb-api-utils main ❯
```