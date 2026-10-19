def resolver(segundos):
    h = segundos // 3600
    m = segundos % 3600 // 60
    s = segundos % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
