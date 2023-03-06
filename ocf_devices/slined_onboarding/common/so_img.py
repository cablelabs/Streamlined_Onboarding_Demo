# Copyright (c) 2023 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed in accordance of the accompanied LICENSE.txt or LICENSE.md
# file in the base directory for this project. If none is supplied contact
# CableLabs for licensing terms of this software.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from PyQt5 import QtWidgets, QtCore

logger = logging.getLogger(__name__)

class SoImgLabel(QtWidgets.QLabel):
    def __init__(self, img=None):
        super().__init__()
        self.img = img

    def set_img(self, img):
        self.img = img
        if img is None:
            self.clear()
        self._scale_img()

    def resizeEvent(self, event):
        self._scale_img()

    def _scale_img(self):
        if self.img is None:
            return
        self.setPixmap(self.img.scaled(self.size(), QtCore.Qt.KeepAspectRatio))
