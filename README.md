# kata

Um desafio de lógica por dia, sem IA. Abre pela waybar como um tile do sway:
editor à esquerda; enunciado e critérios de aceite à direita; statusline no rodapé.

- `kata`: abre o desafio do dia (Ctrl+Enter roda, Ctrl+H dá uma dica, Ctrl+, abre a config, Esc fecha)
- `kata status`: JSON para a waybar
- `kata lembrete`: notifica se o desafio de hoje estiver pendente (timer do systemd)
- `kata treino N`: refaz um desafio já resolvido, sem XP e sem afetar a ofensiva

## Regras

- O desafio do dia é o próximo não resolvido. Resolveu, a janela trava até amanhã.
- Ofensiva: dias seguidos resolvendo. A cada 7 dias seguidos, ganha ❄️ (máx. 2), gasto sozinho num dia perdido.
- XP por nível do desafio, com bônus por passar de primeira e por não usar dica. Cada dica custa XP.
- Colar texto de fora do editor está bloqueado (copiar/colar dentro dele funciona).
- Critérios de aceite: cinza = ainda não atendido, verde = passou, vermelho = falhou.
  Os de código (nomes proibidos, recursão) atualizam enquanto você digita.
- Config (Ctrl+,): progresso, mapa dos dias, conquistas, cronômetro e o caderno.
- Enquanto a janela está aberta, o swaync fica em não perturbe.

## Como a validação funciona

O código roda num sandbox bubblewrap (sem rede, sem $HOME, com limite de tempo e memória).
Os casos ocultos ficam no banco só como `sha256(slug:saída)`: dá para saber se acertou,
mas não qual é a resposta. As soluções de referência ficam em `autoria/`, que o app não usa.

## Arquivos

- `data/desafios.db`: gerado por `python3 autoria/build.py`
- `~/.local/share/kata/progresso.db`: seu progresso, rascunhos e o caderno
- `extras/`: timer do systemd (instalado em `~/.config/systemd/user/`)
- Waybar `custom/kata` (sinal 11), regra do sway `app_id="^local\.kata"` (tile sem borda)

Novos desafios: ver `autoria/AGENTS.md`.

Dependências: python-gobject, gtk4, libadwaita, bubblewrap; opcionais `gtksourceview5`
(cores e números de linha no editor) e `ruff` (lint).

Testes: `python3 -m unittest discover -s tests -t .`

## Instalação

Não tem compilação: o build é só gerar o banco (`data/desafios.db` fica fora do git).

```sh
sudo pacman -S python-gobject gtk4 libadwaita bubblewrap gtksourceview5 ruff
python3 autoria/build.py
ln -sf "$PWD/bin/kata" ~/.local/bin/kata
ln -sf "$PWD"/extras/kata-lembrete.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now kata-lembrete.timer
```

`KATA_DESAFIOS=/caminho/desafios.db` usa um banco em outro lugar.

## Fora do sway

O que é do sway, e o que trocar:

| O quê | Onde | GNOME | KDE | Hyprland / wlroots |
|---|---|---|---|---|
| Não perturbe (swaync) | `App._foco` em `kata/app.py` | `gsettings set org.gnome.desktop.notifications show-banners false/true` | DBus `org.freedesktop.Notifications` (Inhibit) | `makoctl mode -a/-r do-not-disturb`, `dunstctl set-paused true/false` |
| Ícone na barra (waybar, sinal 11) | `SINAL_WAYBAR` e `kata status` | extensão tipo Executor rodando `kata status` | widget Command Output | waybar, igual |
| Tile sem borda | config do WM, `app_id` `local.kata` | não tem tile | Regras de janela do KWin | `windowrulev2 = tile, class:^(local\.kata)$` |
| Paleta | `PALETA` (`~/.config/sway/palette.json`) | sem o arquivo, usa `PALETA_PADRAO` | idem | idem |
| Fonte e ícones | `FONTE` (Terminess Nerd Font Mono) | instalar ou trocar por outra Nerd Font | idem | idem |

O app não desenha barra de título própria. No GNOME (sem decoração do servidor), adicione um
`Adw.HeaderBar` na `Janela`. Para só rodar, sem integração: `KATA_SEM_DND=1 kata`. Sem waybar
ou paleta, o resto falha em silêncio e vira uma janela comum. O lembrete (`notify-send` + systemd)
funciona em qualquer ambiente.
