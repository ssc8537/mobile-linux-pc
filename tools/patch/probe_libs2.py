import io, pickle

ROOT = r'C:\Users\Administrator\Desktop\1-test\1-linux-小小容器'
IDX = pickle.load(io.open(ROOT + r'\tools-probe-scripts-deletable\image_index.pkl', 'rb'))
paths = IDX['paths']

low = {}
for p in paths:
    low[p.rsplit('/', 1)[-1].lower()] = p

for lib in ['libxtst.so.6', 'libgdk-pixbuf-2.0.so.0', 'libgdk_pixbuf-2.0.so.0',
            'libqrencode.so.4', 'libxtst.so', 'libwnck-3.so.0', 'libxfconf-0.so.3',
            'libxmu.so.6', 'libcairo-gobject.so.2', 'libwayland-client.so.0']:
    print(('OK  ' if lib in low else 'MISS'), lib, low.get(lib, ''))
