from brg_rhino.forms import Form

try:
    from System.Windows.Forms import PictureBox
    from System.Windows.Forms import PictureBoxSizeMode
    from System.Windows.Forms import DockStyle
    from System.Drawing import Image

except ImportError as e:

    import platform
    if platform.system() == 'Windows':
        raise e


__author__     = ['Tom Van Mele', ]
__copyright__  = 'Copyright 2014, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'vanmelet@ethz.ch'


__all__ = ['ImageForm', ]


class ImageForm(Form):
    """"""

    def __init__(self, imagepath, title='ImageForm'):
        self.imagepath = imagepath
        super(ImageForm, self).__init__(title)

    def init(self):
        box = PictureBox()
        box.Dock = DockStyle.Fill
        box.SizeMode = PictureBoxSizeMode.AutoSize
        box.Image = Image.FromFile(self.imagepath)
        self.image = box.Image
        self.Controls.Add(box)
        self.ClientSize = box.Size

    def on_form_closed(self, sender, e):
        self.image.Dispose()


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    form = ImageForm('./data/image.gif')
    form.show()
