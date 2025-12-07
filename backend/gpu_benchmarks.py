"""
Mapeo de GPUs a URLs de TechPowerUp (TPU) Specs.
URLs actualizadas a la base de datos de TechPowerUp para una mayor estabilidad.
"""

GPU_BENCHMARK_URLS = {
    # NVIDIA RTX 50 Series (Especulativas)
    'RTX 5090': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-5090.c4216',
    'RTX 5080': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-5080.c4217',
    'RTX 5070 Ti': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-5070-ti.c4243',
    'RTX 5070': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-5070.c4218',
    'RTX 5060 Ti': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-5060-ti-16-gb.c4292',
    'RTX 5060': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-5060.c4219',
    
    # NVIDIA RTX 40 Series (TechPowerUp Specs)
    'RTX 4090': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4090.c3889',
    'RTX 4080 SUPER': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4080-super.c4182',
    'RTX 4080': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4080.c3888',
    'RTX 4070 Ti SUPER': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4070-ti-super.c4187',
    'RTX 4070 Ti': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4070-ti.c3950',
    'RTX 4070 SUPER': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4070-super.c4186',
    'RTX 4070': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4070.c3924',
    'RTX 4060 Ti': 'https://www.techpowerup.com/review/nvidia-geforce-rtx-4060-ti-16-gb/',
    'RTX 4060': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-4060.c4107',
    
    # NVIDIA RTX 30 Series (TechPowerUp Specs)
    'RTX 3090': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-3090.c3622',
    'RTX 3080 Ti': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-3080-ti.c3735',
    'RTX 3080': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-3080.c3621',
    'RTX 3070': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-3070.c3675',
    'RTX 3060 Ti': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-3060-ti.c3681',
    'RTX 3060': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-3060.c3682',
    'RTX 3050': 'https://www.techpowerup.com/gpu-specs/geforce-rtx-3050.c3858',
    
    # AMD RX 9000 Series (Especulativas)
    'RX 9070 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-9070-xt.c4229',
    'RX 9070': 'https://www.techpowerup.com/gpu-specs/radeon-rx-9070.c4250',
    'RX 9060 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-9060-xt-16-gb.c4293',
    'RX 9060': 'https://www.techpowerup.com/gpu-specs/radeon-rx-9060.c4326',
    
    # AMD RX 7000 Series (TechPowerUp Specs)
    'RX 7900 XTX': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7900-xtx.c3941',
    'RX 7900 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7900-xt.c3912',
    'RX 7900': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7900-gre.c4166', 
    'RX 7800 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7800-xt.c3839',
    'RX 7700 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7700-xt.c3911',
    'RX 7700': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7700.c4159', 
    'RX 7600 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7600-xt.c4190',
    'RX 7600': 'https://www.techpowerup.com/gpu-specs/radeon-rx-7600.c4153',
    
    # AMD RX 6000 Series (TechPowerUp Specs)
    'RX 6800 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-6800-xt.c3694',
    'RX 6800': 'https://www.techpowerup.com/gpu-specs/radeon-rx-6800.c3713',
    'RX 6750 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-6750-xt.c3879',
    'RX 6700 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-6700-xt.c3695',
    'RX 6700': 'https://www.techpowerup.com/gpu-specs/radeon-rx-6700.c3716',
    'RX 6600 XT': 'https://www.techpowerup.com/gpu-specs/radeon-rx-6600-xt.c3774',
    'RX 6600': 'https://www.techpowerup.com/gpu-specs/radeon-rx-6600.c3696',
    
    # Intel Arc (TechPowerUp Specs)
    'Arc B580': 'https://www.techpowerup.com/gpu-specs/arc-b580.c4244', 
    'Arc A770': 'https://www.techpowerup.com/gpu-specs/arc-a770.c3914',
    'Arc A750': 'https://www.techpowerup.com/gpu-specs/arc-a750.c3929',
    
    # NVIDIA Legacy (TechPowerUp Specs)
    'GTX 1660 SUPER': 'https://www.techpowerup.com/gpu-specs/geforce-gtx-1660-super.c3458',
    'GTX 1660': 'https://www.techpowerup.com/gpu-specs/geforce-gtx-1660.c3365',
    'GT 710': 'https://www.techpowerup.com/gpu-specs/geforce-gt-710.c1990',
}

# La función para obtener la URL no necesita cambios, ya que solo lee del diccionario
def get_gpu_benchmark_url(gpu_chipset):
    """
    Obtiene la URL de TechPowerUp Specs para una GPU según su chipset.
    Busca coincidencias exactas y parciales en el diccionario.
    
    Args:
        gpu_chipset (str): Nombre del chipset de la GPU (ej: "GeForce RTX 4090")
    
    Returns:
        str: URL de la página de especificaciones (o 'PENDIENTE_LANZAMIENTO') o None si no encuentra coincidencia
    """
    if not gpu_chipset:
        return None
    
    gpu_chipset_upper = gpu_chipset.strip().upper()
    
    # Búsqueda exacta primero
    for model, url in GPU_BENCHMARK_URLS.items():
        if model.upper() == gpu_chipset_upper:
            return url
    
    # Búsqueda parcial (mejor coincidencia)
    best_match_url = None
    best_match_len = 0
    
    for model, url in GPU_BENCHMARK_URLS.items():
        if model.upper() in gpu_chipset_upper:
            if len(model) > best_match_len:
                best_match_url = url
                best_match_len = len(model)
    
    return best_match_url