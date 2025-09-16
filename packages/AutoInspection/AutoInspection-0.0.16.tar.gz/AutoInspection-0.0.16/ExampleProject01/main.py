import time
from pathlib import Path

import hexss
import hexss.path

hexss.check_packages(
    'numpy', 'opencv-python', 'Flask', 'requests', 'pygame', 'pygame-gui',
    'tensorflow', 'keras', 'pyzbar', 'AutoInspection', 'matplotlib',
    'flatbuffers==23.5.26',
    auto_install=True
)

import cv2
import numpy as np
from hexss import json_load, close_port, system, username
from hexss.server import camera_server
from hexss.image import Image
from AutoInspection import AutoInspection, training
from AutoInspection.server import run_server, download_static_files


def capture(data):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def apply_clahe(bgr):
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)
        L = clahe.apply(L)
        lab = cv2.merge([L, A, B])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # ---- Option B: Local tone mapping (compress highlights, lift shadows) ----
    def tone_map_local(bgr, shadow=0.5, highlight=0.6, sigma=15):
        """
        shadow   : 0..1  (higher -> stronger lift for dark areas)
        highlight: 0..1  (higher -> stronger compression for bright areas)
        sigma    : Gaussian sigma for the base layer (larger -> more global)
        """
        f = bgr.astype(np.float32) / 255.0
        # luminance (BT.709)
        Y = 0.2126 * f[..., 2] + 0.7152 * f[..., 1] + 0.0722 * f[..., 0]
        base = cv2.GaussianBlur(Y, (0, 0), sigmaX=sigma, sigmaY=sigma)
        mid = 0.5
        eps = 1e-6

        gain = np.ones_like(base, dtype=np.float32)
        shadows_mask = base < mid
        highlights_mask = ~shadows_mask

        # lift shadows: bring base up toward 0.5
        gain[shadows_mask] = (mid / (base[shadows_mask] + eps)) ** shadow
        # compress highlights: bring base down toward 0.5
        gain[highlights_mask] = (mid / (base[highlights_mask] + eps)) ** highlight

        out = f * gain[..., None]
        out = np.clip(out, 0.0, 1.0)
        return (out * 255.0).astype(np.uint8)

    while data['play']:
        try:
            im1 = Image('http://127.0.0.1:2002/image?source=video_capture&id=0&quality=100')
            im2 = Image('http://127.0.0.1:2002/image?source=video_capture&id=1&quality=100')

            im1.rotate(-90, expand=True)
            im2.rotate(-90, expand=True)

            img1 = tone_map_local(im1.numpy(), shadow=0.75, highlight=0.75, sigma=20)
            img2 = tone_map_local(im2.numpy(), shadow=0.75, highlight=0.75, sigma=20)
            img = np.concatenate((img1, img2), axis=1)
        except:
            img = np.full([3264, 4896, 3], [50, 50, 50], np.uint8)
        data['img'] = img


def main(data):
    app = AutoInspection(data)
    app.run()


if __name__ == '__main__':
    from hexss.threading import Multithread
    from hexss.env import set_proxy, unset_proxy

    set_proxy()
    download_static_files()
    unset_proxy()

    config = json_load('config.json', {
        'projects_directory': r'C:\PythonProjects' if system == 'Windows' else f'/home/{username}/PythonProjects',
        'ipv4': '0.0.0.0',
        'port': 3000,
        'resolution_note': '1920x1080, 800x480',
        'resolution': '1920x1080' if system == 'Windows' else '800x480',
        'model_name': '-',
        'model_names': ["QC7-7990-000-Example", ],
        'fullscreen': True,
    }, True)

    close_port(config['ipv4'], config['port'], verbose=False)

    # download example
    if 'auto_inspection_data__QC7-7990-000-Example' not in \
            list(p.name for p in Path(config['projects_directory']).iterdir()):
        from hexss.github import download

        download(
            'hexs', 'auto_inspection_data__QC7-7990-000-Example',
            dest_dir=Path(config['projects_directory']) / 'auto_inspection_data__QC7-7990-000-Example'
        )

    # training
    try:
        training(
            *config['model_names'],
            config={
                'projects_directory': config['projects_directory'],
                'batch_size': 32,
                'img_height': 180,
                'img_width': 180,
                'epochs': 10,
                'shift_values': [-4, 0, 4],
                'brightness_values': [-12, 0, 12],
                'contrast_values': [-6, 0, 6],
                'max_file': 20000,
            }
        )
    except Exception as e:
        print(e)

    m = Multithread()
    data = {
        'config': config,
        'model_name': config['model_name'],
        'model_names': config['model_names'],
        'events': [],
        'play': True,

    }
    m.add_func(camera_server.run, join=False)
    m.add_func(capture, args=(data,))
    m.add_func(main, args=(data,))
    m.add_func(run_server, args=(data,), join=False)

    m.start()
    try:
        while data['play']:
            # print(m.get_status())
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        data['play'] = False
        m.join()
