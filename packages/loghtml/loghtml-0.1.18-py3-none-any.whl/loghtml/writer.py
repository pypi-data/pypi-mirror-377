import os
import sys
import time
import threading
import importlib
from datetime import datetime

from . import config


def get_local_timestamp():
    x = datetime.now()
    return "%04d-%02d-%02d %02d:%02d:%02d.%03d" % (x.year, x.month, x.day, x.hour, x.minute, x.second, x.microsecond / 1000)


class LogWriter:
    def __init__(self):
        os.makedirs(config.log_dir, exist_ok=True)
        self.trace_file = None
        self.__last_color = None
        self.last_flush = 0
        self.trace_lock = threading.Lock()
        self.current_size = 0
        self._remove_existing_footer()

    def _get_filename(self):
        return os.path.join(config.log_dir, config.main_filename)

    def _remove_existing_footer(self):
        filename = self._get_filename()
        if os.path.exists(filename):
            try:
                with open(filename, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    footer = "<!-- CONTAINER_END -->\n</div>\n</body>\n</html>"
                    if content.endswith(footer):
                        new_content = content[:-len(footer)]
                        f.seek(0)
                        f.write(new_content)
                        f.truncate()
            except Exception:
                pass

    def _load_template(self):
        # Use importlib.resources to access the template file, which is the robust way
        # to access package data, especially with installers like PyInstaller.
        try:
            # Python 3.9+ approach
            if hasattr(importlib.resources, 'files'):
                template_path = importlib.resources.files('loghtml').joinpath(config.template_file)
                content = template_path.read_text(encoding='utf-8')
            # Fallback for Python 3.8
            else:
                content = importlib.resources.read_text('loghtml', config.template_file, encoding='utf-8')

            return content.replace('<!-- CONTAINER_END --></div></body></html>', '')
        except (FileNotFoundError, ModuleNotFoundError):
            # Ultimate fallback to a default template if the file is not found.
            # This can happen if the package is not installed correctly or if
            # PyInstaller fails to bundle the data file.
            return """<!DOCTYPE html PUBLIC "v0.1.16">
<meta charset="utf-8" />

<style>
  body {
    color: white;
    background-color: black;
    font-family: monospace, sans-serif;
    margin: 0;
    padding: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .filter-panel {
    display: none;
    position: fixed;
    top: 80px;
    right: 20px;
    background-color: #2c2c2c;
    border: 1px solid #444;
    padding: 15px;
    border-radius: 8px;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    width: 350px;
    max-height: 80vh;
    overflow-y: auto;
    white-space: normal;
  }
  .filter-tabs {
    display: flex;
    margin-bottom: 10px;
    border-bottom: 1px solid #444;
  }
  .filter-tab {
    padding: 8px 15px;
    cursor: pointer;
    background: none;
    border: none;
    color: #ccc;
    flex: 1;
    text-align: center;
  }
  .filter-tab.active {
    color: #4caf50;
    border-bottom: 2px solid #4caf50;
  }
  .filter-content {
    display: none;
  }
  .filter-content.active {
    display: block;
  }
  .filter-input {
    width: 100%;
    padding: 8px;
    background-color: #1a1a1a;
    color: white;
    border: 1px solid #444;
    border-radius: 4px;
    margin-bottom: 10px;
    box-sizing: border-box;
  }
  .filter-help {
    font-size: 12px;
    color: #888;
    margin-bottom: 10px;
  }
  .filter-types {
    max-height: 200px;
    overflow-y: auto;
    margin-bottom: 10px;
  }
  .type-checkbox {
    margin: 5px 0;
    display: block;
  }
  .type-checkbox input {
    margin-right: 8px;
  }
  .filter-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: rgba(255, 255, 255, 0.8);
    color: #333;
    border: 3px solid #2bd331;
    border-radius: 8px;
    width: 50px;
    height: 50px;
    font-size: 24px;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    transition: background-color 0.3s, border-color 0.3s;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .filter-btn:hover {
    background-color: rgba(180, 180, 180, 0.9);
    border-color: #45a049;
  }
  .highlight {
    background-color: yellow;
    color: black;
    padding: 0 2px;
  }
  .log-line {
    margin: 0;
  }
  .visible {
    display: block;
  }
  .hidden {
    display: none;
  }
  .filter-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
  }
  .filter-action-btn {
    padding: 8px 16px;
    font-size: 14px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s, transform 0.1s;
  }
  .filter-action-btn:hover {
    transform: translateY(-1px);
  }
  .filter-action-btn.apply {
    background-color: #4caf50;
    color: white;
  }
  .filter-action-btn.clear {
    background-color: #f44336;
    color: white;
  }
  .filter-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 15px;
    border-top: 1px solid #444;
    padding-top: 10px;
  }
  #filteredContainer .log-line {
    display: block;
    margin: 0;
  }
  font {
    white-space: pre;
    display: block;
  }
  #logContainer {
    flex: 1;
    overflow-x: auto;
    white-space: nowrap;
    align-self: flex-start;
    width: 100%;
  }
</style>

<body>
  <div id="filterPanel" class="filter-panel">
    <div class="filter-tabs">
      <button class="filter-tab active" data-tab="text">Text Filter</button>
      <button class="filter-tab" data-tab="type">Filter by Tag</button>
    </div>

    <div id="textFilter" class="filter-content active">
      <input
        type="text"
        id="textFilterInput"
        class="filter-input"
        placeholder="Digite para filtrar (usar AND, OR)..."
      />
      <div class="filter-help">
        Use AND, OR para filtros complexos. Ex: "error AND security", "warning OR info"
      </div>
    </div>

    <div id="typeFilter" class="filter-content">
      <div id="typeFilterList" class="filter-types">
        <!-- Checkboxes -->
      </div>
      <div class="filter-actions">
        <button id="selectAllTypes" class="filter-action-btn apply">
          Select All
        </button>
        <button id="deselectAllTypes" class="filter-action-btn clear">
          Clear Selection
        </button>
      </div>
    </div>

    <div class="filter-footer">
      <button id="applyFiltersBtn" class="filter-action-btn apply">
        Apply Filters
      </button>
      <button id="clearFiltersBtn" class="filter-action-btn clear">
        Reset View
      </button>
    </div>
  </div>

  <button id="filterBtn" class="filter-btn">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 4H21L14 12V20L10 22V12L3 4Z" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>

  <script>
    let USED_TAGS = [];
    let activeFilters = { text: "", types: [] };
    let filterModeEnabled = false;

    function notifyFilterModeChange(enabled) {
      if (filterModeEnabled !== enabled) {
        filterModeEnabled = enabled;

        let signalDiv = document.getElementById('filterModeSignal');
        if (!signalDiv) {
          signalDiv = document.createElement('div');
          signalDiv.id = 'filterModeSignal';
          signalDiv.style.display = 'none';
          document.body.appendChild(signalDiv);
        }

        signalDiv.setAttribute('data-filter-active', enabled.toString());
        signalDiv.textContent = `FILTER_MODE:${enabled}:${Date.now()}`;
      }
    }

    function extractTagsFromDOM() {
      const tagSet = new Set();
      const elements = document.querySelectorAll("#logContainer [tag]");
      elements.forEach((element) => {
        const tags = element.getAttribute("tag").split(",");
        tags.forEach((tag) => tagSet.add(tag.trim()));
      });
      USED_TAGS = Array.from(tagSet).sort();
    }

    function initTypeFilter() {
      const typeFilterList = document.getElementById("typeFilterList");
      typeFilterList.innerHTML = "";
      USED_TAGS.forEach((tag) => {
        const label = document.createElement("label");
        label.className = "type-checkbox";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = tag;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(tag));
        typeFilterList.appendChild(label);
      });
    }

    function setupTabs() {
      const tabs = document.querySelectorAll(".filter-tab");
      const tabContents = document.querySelectorAll(".filter-content");
      tabs.forEach((tab) => {
        tab.addEventListener("click", function () {
          const tabName = this.getAttribute("data-tab");
          tabs.forEach((t) => t.classList.remove("active"));
          this.classList.add("active");
          tabContents.forEach((content) => content.classList.remove("active"));
          document.getElementById(`${tabName}Filter`).classList.add("active");
          if (tabName === "text") {
            document.getElementById("textFilterInput").focus();
          }
        });
      });
    }

    function applyFilters() {
      activeFilters.text = document.getElementById("textFilterInput").value;
      activeFilters.types = Array.from(
        document.querySelectorAll("#typeFilterList input:checked")
      ).map((cb) => cb.value);

      const hasFilters = activeFilters.text.trim() !== "" || activeFilters.types.length > 0;

      notifyFilterModeChange(hasFilters);

      const lines = document.querySelectorAll("#logContainer [tag]");
      const filteredContainer = document.getElementById("filteredContainer");

      const textRaw = (activeFilters.text || "").trim();
      const hasTextFilter = textRaw !== "";
      const hasTypeFilter = Array.isArray(activeFilters.types) && activeFilters.types.length > 0;

      if (!hasTextFilter && !hasTypeFilter) {
        lines.forEach((line) => {
          if (!line.hasAttribute("data-original-html")) {
            line.setAttribute("data-original-html", line.innerHTML);
          }
          const originalHtml = line.getAttribute("data-original-html");
          line.innerHTML = originalHtml;
        });
        filteredContainer.innerHTML = "";
        document.getElementById("logContainer").style.display = "block";
        document.getElementById("filteredContainer").style.display = "none";
        return;
      }

      let textFilters = [];
      let isAnd = false;
      if (hasTextFilter) {
        const lower = textRaw.toLowerCase();
        if (/\\sand\\s/i.test(lower)) {
          textFilters = lower.split(/\\sand\\s/i).map((s) => s.trim()).filter(Boolean);
          isAnd = true;
        } else if (/\\sor\\s/i.test(lower)) {
          textFilters = lower.split(/\\sor\\s/i).map((s) => s.trim()).filter(Boolean);
        } else {
          textFilters = [lower];
        }
      }

      filteredContainer.innerHTML = "";

      lines.forEach((line) => {
        if (!line.hasAttribute("data-original-html")) {
          line.setAttribute("data-original-html", line.innerHTML);
        }
        const originalHtml = line.getAttribute("data-original-html");
        line.innerHTML = originalHtml;

        const textContent = (line.textContent || line.innerText || "").toLowerCase();
        const lineTags = (line.getAttribute("tag") || "").split(",").map((t) => t.trim()).filter(Boolean);

        let textMatch = !hasTextFilter;
        if (hasTextFilter) {
          if (isAnd) {
            textMatch = textFilters.every((f) => textContent.includes(f));
          } else {
            textMatch = textFilters.some((f) => textContent.includes(f));
          }
        }

        const typeMatch = !hasTypeFilter || activeFilters.types.some((t) => lineTags.includes(t));

        if (textMatch && typeMatch) {
          const wrapper = document.createElement("div");
          wrapper.className = "log-line";
          const copy = line.cloneNode(true);
          wrapper.appendChild(copy);
          filteredContainer.appendChild(wrapper);
        }
      });

      document.getElementById("logContainer").style.display = "none";
      document.getElementById("filteredContainer").style.display = "block";
    }

    function clearFilters() {
      document.getElementById("textFilterInput").value = "";
      document.querySelectorAll("#typeFilterList input").forEach((cb) => (cb.checked = false));
      activeFilters = { text: "", types: [] };

      notifyFilterModeChange(false);

      document.querySelectorAll("#logContainer [tag]").forEach((line) => {
        if (line.hasAttribute("data-original-html")) {
          line.innerHTML = line.getAttribute("data-original-html");
        }
      });

      document.getElementById("logContainer").style.display = "block";
      document.getElementById("filteredContainer").style.display = "none";
      document.getElementById("filteredContainer").innerHTML = "";
    }

    function resetView() {
      document.querySelectorAll("#logContainer [tag]").forEach((line) => {
        if (line.hasAttribute("data-original-html")) {
          line.innerHTML = line.getAttribute("data-original-html");
        }
      });

      document.getElementById("logContainer").style.display = "block";
      document.getElementById("filteredContainer").style.display = "none";
      document.getElementById("filteredContainer").innerHTML = "";

      notifyFilterModeChange(false);
    }

    function clearAllFilters() {
      document.getElementById("textFilterInput").value = "";
      document.querySelectorAll("#typeFilterList input").forEach((cb) => (cb.checked = false));
      activeFilters = { text: "", types: [] };

      resetView();
    }

    document.addEventListener("DOMContentLoaded", function () {
      const filterBtn = document.getElementById("filterBtn");
      const filterPanel = document.getElementById("filterPanel");
      const textFilterInput = document.getElementById("textFilterInput");
      const selectAllBtn = document.getElementById("selectAllTypes");
      const deselectAllBtn = document.getElementById("deselectAllTypes");
      const applyBtn = document.getElementById("applyFiltersBtn");
      const clearBtn = document.getElementById("clearFiltersBtn");

      extractTagsFromDOM();
      initTypeFilter();
      setupTabs();

      filterBtn.addEventListener("click", function () {
        if (filterPanel.style.display === "block") {
          filterPanel.style.display = "none";
        } else {
          extractTagsFromDOM();
          initTypeFilter();
          filterPanel.style.display = "block";
          const activeTab = document.querySelector(".filter-tab.active").getAttribute("data-tab");
          if (activeTab === "text") {
            textFilterInput.focus();
          }
        }
      });

      applyBtn.addEventListener("click", applyFilters);
      clearBtn.addEventListener("click", resetView);

      selectAllBtn.addEventListener("click", function () {
        document.querySelectorAll("#typeFilterList input").forEach((checkbox) => {
          checkbox.checked = true;
        });
      });

      deselectAllBtn.addEventListener("click", function () {
        document.querySelectorAll("#typeFilterList input").forEach((checkbox) => {
          checkbox.checked = false;
        });
      });

      document.addEventListener("click", function (event) {
        if (!filterPanel.contains(event.target) && !filterBtn.contains(event.target)) {
          filterPanel.style.display = "none";
        }
      });

      filterPanel.addEventListener("click", function (event) {
        event.stopPropagation();
      });

      textFilterInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
          applyFilters();
        }
      });
    });
  </script>

  <div id="filteredContainer"></div>

  <div id="logContainer">
"""

    def _remove_extra_files(self, pattern, limit):
        import glob
        try:
            files = glob.glob(pattern)
            if len(files) > limit:
                files.sort()
                for f in files[:-limit]:
                    os.remove(f)
        except Exception:
            pass

    def _handle_new_log_file(self, file_name, file_pattern, fd):
        target = file_pattern % (fd)
        limit_count = config.log_files_limit_count

        target += ".tmp"
        limit_count -= 1

        try:
            os.rename(file_name, target)
        except OSError:
            pass

        self._remove_extra_files(file_pattern % "*", limit_count)

        # Cross-platform file operations
        import platform
        import subprocess
        import glob
        
        try:
            # Compress the target file if gzip is available
            if platform.system() != 'Windows':
                subprocess.run(['gzip', '-c', target], 
                             stdout=open(target[:-4], 'wb'), 
                             stderr=subprocess.DEVNULL,
                             check=False)
            
            # Remove temporary files cross-platform
            os.remove(target) if os.path.exists(target) else None
            
            # Clean up temporary files
            for temp_file in glob.glob("trace_*.dat.tmp") + glob.glob("ErrorLog_*.txt.gz.tmp"):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
                    
        except (subprocess.SubprocessError, OSError):
            # If compression fails, just remove the original file
            try:
                os.remove(target) if os.path.exists(target) else None
            except OSError:
                pass

    def write_direct(self, msg, color, tag):
        escape_table = str.maketrans({
            '<': '&lt;',
            '>': '&gt;'
        })
        msg = msg.translate(escape_table)
        msg = msg.replace('\n', '<br>').replace('\r\n', '<br>').replace('=>', '&rArr;')

        x = datetime.now()
        date_str = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % (x.year, x.month, x.day, x.hour, x.minute, x.second, x.microsecond // 1000)
        _msg = date_str + ' - ' + msg
        formated_msg = f'<font color="{color}" tag="{tag}">{_msg}</font>\n'

        self.trace_lock.acquire()

        filename = self._get_filename()
        if not self.trace_file:
            if os.path.exists(filename):
                self.trace_file = open(filename, 'a', encoding='utf-8')
            else:
                self.trace_file = open(filename, 'w', encoding='utf-8')
                self.trace_file.write(self._load_template())

        try:
            self.trace_file.write(formated_msg)

            # Check if we need to rotate the file
            self.current_size += len(formated_msg)
            if self.current_size >= config.log_files_limit_size:
                self._rotate_file()

        except Exception:
            pass

        try:
            t = time.monotonic()
            if t - self.last_flush > 2:
                self.trace_file.flush()
                self.last_flush = t
        except Exception:
            pass

        self.trace_lock.release()

    def _rotate_file(self):
        """Rotate the log file if it exceeds the size limit"""
        if self.trace_file:
            self.trace_file.write("<!-- CONTAINER_END -->\n</div>\n</body>\n</html>")
            self.trace_file.close()
            self.trace_file = None

            # Create a backup of the current file
            import glob
            from datetime import datetime

            filename = self._get_filename()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = os.path.join(config.log_dir, f"{timestamp}_{config.main_filename}")

            try:
                os.rename(filename, backup_name)
            except OSError:
                pass

            # Remove old files if exceeding the limit
            try:
                pattern = os.path.join(config.log_dir, f"*_{config.main_filename}")
                files = glob.glob(pattern)
                if len(files) > config.log_files_limit_count:
                    files.sort()
                    for f in files[:-config.log_files_limit_count]:
                        os.remove(f)
            except Exception:
                pass

            self.current_size = 0

    def close(self):
        if self.trace_file is None:
            return

        self.trace_lock.acquire()
        try:
            if self.trace_file:
                self.trace_file.write("<!-- CONTAINER_END -->\n</div>\n</body>\n</html>")
                self.trace_file.close()
                self.trace_file = None
        except Exception:
            pass
        finally:
            self.trace_lock.release()
