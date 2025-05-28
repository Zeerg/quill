"""
Report generation module for Quill LLM Fuzzer.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class ReportGenerator:
    """Generate HTML reports from fuzzing results."""

    def __init__(self, results_dir: Path):
        """
        Initialize with the directory containing fuzzing results.

        Args:
            results_dir: Path to the directory containing fuzzing results
        """
        self.results_dir = results_dir
        self.config = self._load_config()
        self.summary = self._load_summary()
        self.prompt_results = self._load_prompt_results()

    def _load_config(self) -> Dict[str, Any]:
        """Load the run configuration."""
        config_path = self.results_dir / "config.json"
        if not config_path.exists():
            return {}

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_summary(self) -> Dict[str, Any]:
        """Load the summary statistics."""
        summary_path = self.results_dir / "summary.json"
        if not summary_path.exists():
            return {}

        with open(summary_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_prompt_results(self) -> List[Dict[str, Any]]:
        """Load all prompt results."""
        results = []

        for file_path in sorted(self.results_dir.glob("prompt_*.json")):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    result = json.load(f)
                    results.append(result)
                except json.JSONDecodeError:
                    continue

        # Sort by index
        results.sort(key=lambda x: x.get("index", 0))
        return results

    def generate_html_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate an HTML report from the fuzzing results.

        Args:
            output_path: Path to save the HTML report to
                         If None, saves to results_dir/report.html

        Returns:
            Path to the generated HTML report
        """
        if output_path is None:
            output_path = self.results_dir / "report.html"

        html_content = self._generate_html()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

    def _get_logo_svg(self) -> str:
        """Return a simple SVG version of the Quill logo."""
        # Simple SVG feather icon representing Quill
        return """<svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5l6.74-6.76zM16 8L8.5 15.5M16 12L12 16"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""

    def _generate_html(self) -> str:
        """Generate the HTML content."""
        # Load template
        css = self._get_css()
        logo_svg = self._get_logo_svg()

        # Prepare data for template
        run_time = datetime.datetime.fromtimestamp(self.config.get("time", 0))
        completion_time = datetime.datetime.fromtimestamp(
            self.summary.get("completed_time", 0)
        )
        duration = completion_time - run_time if completion_time and run_time else None

        # Format duration as minutes and seconds
        duration_str = ""
        if duration:
            minutes = duration.seconds // 60
            seconds = duration.seconds % 60
            duration_str = f"{minutes}m {seconds}s"

        # Calculate stats
        total_prompts = self.summary.get("total_prompts", 0)
        anomalies = self.summary.get("anomalies", 0)
        anomaly_rate = self.summary.get("anomaly_rate", 0) * 100

        refusals = sum(1 for r in self.prompt_results if r.get("is_refusal", False))
        refusal_rate = (refusals / total_prompts) * 100 if total_prompts > 0 else 0

        mutations = sum(
            1 for r in self.prompt_results if r.get("mutation_applied", False)
        )
        mutation_rate = (mutations / total_prompts) * 100 if total_prompts > 0 else 0

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quill LLM Fuzzer Report</title>
    <style>
    {css}
    </style>
</head>
<body>
    <!-- Theme toggle button -->
    <div class="theme-toggle" id="themeToggle">
        <div class="theme-toggle-switch"></div>
    </div>

    <div class="container">
        <header>
            <div class="logo">
                {logo_svg}
            </div>
            <h1>Quill LLM Fuzzer Report</h1>
            <p class="subtitle">Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <section class="summary">
            <div class="section-header" onclick="toggleSection('summaryContent')">
                <h2>Run Summary</h2>
                <span class="section-toggle">▼</span>
            </div>
            <div id="summaryContent" class="section-content expanded">
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-value">{total_prompts}</div>
                        <div class="stat-label">Total Prompts</div>
                    </div>
                    <div class="stat-card highlight">
                        <div class="stat-value">{anomalies}</div>
                        <div class="stat-label">Anomalies</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{refusals}</div>
                        <div class="stat-label">Refusals</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{mutations}</div>
                        <div class="stat-label">Mutations</div>
                    </div>
                </div>

                <div class="metrics-container">
                    <div class="metric">
                        <span class="metric-label">Anomaly Rate:</span>
                        <div class="progress-bar">
                            <div class="progress" style="width: {anomaly_rate}%;"></div>
                        </div>
                        <span class="metric-value">{anomaly_rate:.2f}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Refusal Rate:</span>
                        <div class="progress-bar">
                            <div class="progress" style="width: {refusal_rate}%;"></div>
                        </div>
                        <span class="metric-value">{refusal_rate:.2f}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Mutation Rate:</span>
                        <div class="progress-bar">
                            <div class="progress" style="width: {mutation_rate}%;"></div>
                        </div>
                        <span class="metric-value">{mutation_rate:.2f}%</span>
                    </div>
                </div>
            </div>
        </section>

        <section class="config">
            <div class="section-header" onclick="toggleSection('configContent')">
                <h2>Configuration</h2>
                <span class="section-toggle">▼</span>
            </div>
            <div id="configContent" class="section-content expanded">
                <div class="config-details">
                    <div class="config-item">
                        <span class="config-label">Mode:</span>
                        <span class="config-value">{self.config.get("mode", "N/A")}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Model:</span>
                        <span class="config-value">{self.config.get("model_id", "N/A")}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">URL:</span>
                        <span class="config-value">{self.config.get("url", "N/A")}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Temperature:</span>
                        <span class="config-value">{self.config.get("temperature", "N/A")}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Mutators:</span>
                        <span class="config-value">{", ".join(self.config.get("mutators", ["N/A"]))}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Run Time:</span>
                        <span class="config-value">{run_time.strftime('%Y-%m-%d %H:%M:%S') if run_time else "N/A"}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Duration:</span>
                        <span class="config-value">{duration_str if duration_str else "N/A"}</span>
                    </div>
                </div>
            </div>
        </section>

        <section class="prompts">
            <div class="section-header-static">
                <h2>Prompt Results</h2>
            </div>
            <div class="section-content-static">
                <div class="search-container">
                    <input type="text" id="searchInput" placeholder="Search prompts, responses..." class="search-input">
                    <div class="search-controls">
                        <label><input type="checkbox" id="anomalyFilter" checked> Anomalies</label>
                        <label><input type="checkbox" id="refusalFilter" checked> Refusals</label>
                        <label><input type="checkbox" id="mutationFilter" checked> Mutations</label>
                        <label><input type="checkbox" id="normalFilter" checked> Normal</label>
                    </div>
                </div>

            <div class="result-cards-container">
                <div class="search-header">
                    <div class="result-card result-header">
                        <div class="result-index">#</div>
                        <div class="result-type">Type</div>
                        <div class="result-original">Original Prompt</div>
                        <div class="result-mutated">Mutated Prompt</div>
                        <div class="result-response">Response</div>
                        <div class="result-actions">Actions</div>
                    </div>
                </div>
                <div id="resultsContainer" class="results-container">
"""

        # Add table rows
        for result in self.prompt_results:
            row_class = ""
            if result.get("is_anomaly", False):
                row_class += " anomaly"
            if result.get("is_refusal", False):
                row_class += " refusal"
            if result.get("mutation_applied", False):
                row_class += " mutation"

            if not row_class:
                row_class = " normal"

            original = result.get("original", "")
            mutated = result.get("mutated", "")
            response = result.get("response", "")
            index = result.get("index", 0)

            # Truncate response for display
            max_preview_length = 80
            original_preview = (
                (original[:max_preview_length] + "...")
                if len(original) > max_preview_length
                else original
            )
            mutated_preview = (
                (mutated[:max_preview_length] + "...")
                if len(mutated) > max_preview_length
                else mutated
            )
            response_preview = (
                (response[:max_preview_length] + "...")
                if len(response) > max_preview_length
                else response
            )

            # Escape HTML entities
            original = original.replace("<", "&lt;").replace(">", "&gt;")
            mutated = mutated.replace("<", "&lt;").replace(">", "&gt;")
            response = response.replace("<", "&lt;").replace(">", "&gt;")
            original_preview = original_preview.replace("<", "&lt;").replace(
                ">", "&gt;"
            )
            mutated_preview = mutated_preview.replace("<", "&lt;").replace(">", "&gt;")
            response_preview = response_preview.replace("<", "&lt;").replace(
                ">", "&gt;"
            )

            badges = []
            if result.get("is_anomaly", False):
                badges.append('<span class="badge anomaly-badge">Anomaly</span>')
            if result.get("is_refusal", False):
                badges.append('<span class="badge refusal-badge">Refusal</span>')
            if result.get("mutation_applied", False):
                badges.append('<span class="badge mutation-badge">Mutated</span>')

            if not badges:
                badges.append('<span class="badge normal-badge">Normal</span>')

            html += f"""
                    <div class="result-card{row_class}"
                         data-index="{index}"
                         data-original="{original}"
                         data-mutated="{mutated}"
                         data-response="{response}">
                        <div class="result-index">{index}</div>
                        <div class="result-type">{''.join(badges)}</div>
                        <div class="result-original">{original_preview}</div>
                        <div class="result-mutated">{mutated_preview}</div>
                        <div class="result-response">{response_preview}</div>
                        <div class="result-actions">
                            <button class="view-btn" onclick="viewDetails({index})">View</button>
                        </div>
                    </div>
"""

        # Add detail modal and close HTML
        html += """
                </div>
            </div>

            <div class="pagination">
                <button id="prevPage">Previous</button>
                <span id="pageIndicator">Page 1 of 1</span>
                <button id="nextPage">Next</button>
                <select id="pageSize">
                    <option value="10">10 per page</option>
                    <option value="20" selected>20 per page</option>
                    <option value="50">50 per page</option>
                    <option value="100">100 per page</option>
                </select>
            </div>
            </div>
        </section>

        <!-- Detail Modal -->
        <div id="detailModal" class="modal">
            <div class="modal-content">
                <span class="close-btn" onclick="closeModal()">&times;</span>
                <h3 id="modalTitle">Prompt #0</h3>
                <div class="modal-badges" id="modalBadges"></div>

                <div class="modal-section">
                    <div class="section-header" onclick="toggleSection('modalOriginalSection')">
                        <h4>Original Prompt</h4>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div id="modalOriginalSection" class="section-content expanded">
                        <pre id="modalOriginal"></pre>
                    </div>
                </div>

                <div class="modal-section">
                    <div class="section-header" onclick="toggleSection('modalMutatedSection')">
                        <h4>Mutated Prompt</h4>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div id="modalMutatedSection" class="section-content expanded">
                        <pre id="modalMutated"></pre>
                    </div>
                </div>

                <div class="modal-section">
                    <div class="section-header" onclick="toggleSection('modalResponseSection')">
                        <h4>Response</h4>
                        <span class="section-toggle">▼</span>
                    </div>
                    <div id="modalResponseSection" class="section-content expanded">
                        <pre id="modalResponse"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Theme toggle functionality
        const themeToggle = document.getElementById('themeToggle');
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

        // Set initial theme based on system preference
        if (prefersDarkMode) {
            document.body.classList.add('dark-mode');
        }

        // Toggle theme on click
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
        });

        // Table pagination functionality
        let currentPage = 1;
        let pageSize = 20;
        let filteredRows = [];

        function updateTable() {
            const container = document.getElementById('resultsContainer');
            const cards = Array.from(container.querySelectorAll('.result-card'));
            filteredRows = cards.filter(card => {
                // Apply checkbox filters
                const isAnomaly = card.classList.contains('anomaly');
                const isRefusal = card.classList.contains('refusal');
                const isMutation = card.classList.contains('mutation');
                const isNormal = !isAnomaly && !isRefusal && !isMutation;

                const showAnomalies = document.getElementById('anomalyFilter').checked;
                const showRefusals = document.getElementById('refusalFilter').checked;
                const showMutations = document.getElementById('mutationFilter').checked;
                const showNormal = document.getElementById('normalFilter').checked;

                // Apply search filter
                const searchText = document.getElementById('searchInput').value.toLowerCase();
                const cardText = [
                    card.getAttribute('data-original'),
                    card.getAttribute('data-mutated'),
                    card.getAttribute('data-response')
                ].join(' ').toLowerCase();

                const matchesSearch = searchText === '' || cardText.includes(searchText);

                // Combine filters
                return matchesSearch &&
                       ((isAnomaly && showAnomalies) ||
                        (isRefusal && showRefusals) ||
                        (isMutation && showMutations) ||
                        (isNormal && showNormal));
            });

            // Hide all cards
            cards.forEach(card => card.style.display = 'none');

            // Show filtered and paginated cards
            const startIndex = (currentPage - 1) * pageSize;
            const endIndex = Math.min(startIndex + pageSize, filteredRows.length);

            for (let i = startIndex; i < endIndex; i++) {
                filteredRows[i].style.display = 'grid';
            }

            // Update pagination controls
            const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));
            document.getElementById('pageIndicator').textContent = `Page ${currentPage} of ${totalPages}`;
            document.getElementById('prevPage').disabled = currentPage === 1;
            document.getElementById('nextPage').disabled = currentPage === totalPages;
        }

        // Detail modal functionality
        function viewDetails(index) {
            const card = document.querySelector(`.result-card[data-index="${index}"]`);
            if (!card) return;

            document.getElementById('modalTitle').textContent = `Prompt #${index}`;
            document.getElementById('modalOriginal').textContent = card.getAttribute('data-original');
            document.getElementById('modalMutated').textContent = card.getAttribute('data-mutated');
            document.getElementById('modalResponse').textContent = card.getAttribute('data-response');

            // Set badges
            document.getElementById('modalBadges').innerHTML = card.querySelector('.result-type').innerHTML;

            document.getElementById('detailModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('detailModal').style.display = 'none';
        }

        function toggleSection(sectionId) {
            const contentElement = document.getElementById(sectionId);
            const headerElement = contentElement.previousElementSibling;
            const toggleIcon = headerElement.querySelector('.section-toggle');

            if (contentElement.classList.contains('expanded')) {
                contentElement.classList.remove('expanded');
                toggleIcon.classList.add('collapsed');
            } else {
                contentElement.classList.add('expanded');
                toggleIcon.classList.remove('collapsed');
            }
        }

        // Card sorting functionality
        function sortTable(column) {
            const container = document.getElementById('resultsContainer');
            const cards = Array.from(container.querySelectorAll('.result-card:not(.result-header)'));

            const sortedCards = cards.sort((a, b) => {
                const aValue = a.getAttribute(`data-${column}`);
                const bValue = b.getAttribute(`data-${column}`);

                if (column === 'index') {
                    return parseInt(aValue) - parseInt(bValue);
                } else {
                    return aValue.localeCompare(bValue);
                }
            });

            // Update DOM
            container.innerHTML = '';
            sortedCards.forEach(card => container.appendChild(card));

            // Update pagination
            updateTable();
        }

        // Event listeners
        document.addEventListener('DOMContentLoaded', () => {
            // Sort buttons
            document.querySelectorAll('.sortable').forEach(header => {
                header.addEventListener('click', () => {
                    const column = header.getAttribute('data-sort');
                    sortTable(column);
                });
            });

            // Filters
            document.getElementById('searchInput').addEventListener('input', () => {
                currentPage = 1;
                updateTable();
            });

            document.getElementById('anomalyFilter').addEventListener('change', updateTable);
            document.getElementById('refusalFilter').addEventListener('change', updateTable);
            document.getElementById('mutationFilter').addEventListener('change', updateTable);
            document.getElementById('normalFilter').addEventListener('change', updateTable);

            // Pagination
            document.getElementById('prevPage').addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    updateTable();
                }
            });

            document.getElementById('nextPage').addEventListener('click', () => {
                const totalPages = Math.ceil(filteredRows.length / pageSize);
                if (currentPage < totalPages) {
                    currentPage++;
                    updateTable();
                }
            });

            document.getElementById('pageSize').addEventListener('change', (e) => {
                pageSize = parseInt(e.target.value);
                currentPage = 1;
                updateTable();
            });

            // Modal close on click outside
            window.addEventListener('click', (e) => {
                const modal = document.getElementById('detailModal');
                if (e.target === modal) {
                    closeModal();
                }
            });

            // Initialize table
            updateTable();
        });
    </script>
</body>
</html>
"""

        return html

    def _get_css(self) -> str:
        """Get the CSS styles for the report."""
        return """
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Results Card Styling */
        .result-cards-container {
            margin-bottom: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px var(--shadow);
            background-color: var(--surface);
            border: 1px solid var(--border);
            overflow: hidden;
        }

        .search-header {
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .result-card {
            display: grid;
            grid-template-columns: 50px 90px minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) 60px;
            border-bottom: 1px solid var(--border);
            font-size: 0.875rem;
            align-items: start;
        }

        .result-header {
            background-color: var(--surface-alt);
            font-weight: 600;
            padding: 0.75rem 0;
            align-items: center;
            border-bottom: 2px solid var(--border);
        }

        .result-header > div {
            padding: 0 1rem;
            text-align: left;
        }

        .result-card > div {
            padding: 0.75rem 1rem;
            overflow: hidden;
        }

        .result-index {
            font-weight: 600;
            text-align: center;
        }

        .result-type {
            white-space: nowrap;
        }

        .result-original,
        .result-mutated,
        .result-response {
            overflow: hidden;
            word-wrap: break-word;
            white-space: normal;
            line-height: 1.4;
            max-height: 4.2em;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            text-overflow: ellipsis;
            text-align: left;
            padding-top: 1rem;
        }

        .result-actions {
            text-align: center;
        }

        .result-card.anomaly {
            border-left: 3px solid var(--anomaly);
        }

        .result-card.refusal {
            border-left: 3px solid var(--refusal);
        }

        .result-card.mutation {
            border-left: 3px solid var(--mutation);
        }

        .result-card.normal {
            border-left: 3px solid transparent;
        }

        .result-card:not(.result-header):hover {
            background-color: var(--surface-alt);
        }
        
        /* Root variables for theme colors */
        :root {
            /* Light mode */
            --background: #f5f7fa;
            --surface: #ffffff;
            --surface-alt: #f8fafc;
            --border: #e1e4e8;
            --text-primary: #2d3748;
            --text-secondary: #4a5568;
            --text-muted: #718096;
            --primary: #3182ce;
            --primary-light: #4299e1;
            --primary-dark: #2c5282;
            --primary-bg: #ebf8ff;
            --shadow: rgba(0, 0, 0, 0.05);
            --shadow-hover: rgba(0, 0, 0, 0.1);
            --anomaly: #e53e3e;
            --anomaly-bg: #fed7d7;
            --anomaly-text: #c53030;
            --refusal: #805ad5;
            --refusal-bg: #e9d8fd;
            --refusal-text: #6b46c1;
            --mutation: #dd6b20;
            --mutation-bg: #feebc8;
            --mutation-text: #c05621;
            --normal: #718096;
            --normal-bg: #edf2f7;
            --normal-text: #4a5568;
            --code-bg: #2d3748;
            --code-text: #f7fafc;
        }
        
        /* Dark mode */
        .dark-mode {
            --background: #1a202c;
            --surface: #2d3748;
            --surface-alt: #353f50;
            --border: #4a5568;
            --text-primary: #f7fafc;
            --text-secondary: #e2e8f0;
            --text-muted: #a0aec0;
            --primary: #4299e1;
            --primary-light: #63b3ed;
            --primary-dark: #2b6cb0;
            --primary-bg: #2c5282;
            --shadow: rgba(0, 0, 0, 0.2);
            --shadow-hover: rgba(0, 0, 0, 0.4);
            --anomaly: #fc8181;
            --anomaly-bg: #742a2a;
            --anomaly-text: #fc8181;
            --refusal: #b794f4;
            --refusal-bg: #44337a;
            --refusal-text: #b794f4;
            --mutation: #f6ad55;
            --mutation-bg: #7b341e;
            --mutation-text: #f6ad55;
            --normal: #a0aec0;
            --normal-bg: #2d3748;
            --normal-text: #cbd5e0;
            --code-bg: #1a202c;
            --code-text: #f7fafc;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background-color: var(--background);
            padding: 0;
            margin: 0;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Theme toggle */
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            width: 50px;
            height: 26px;
            border-radius: 13px;
            background-color: var(--surface);
            border: 2px solid var(--border);
            cursor: pointer;
            display: flex;
            align-items: center;
            padding: 2px;
            justify-content: flex-start;
            transition: all 0.3s ease;
            z-index: 100;
        }
        
        .dark-mode .theme-toggle {
            justify-content: flex-end;
        }
        
        .theme-toggle-switch {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background-color: var(--primary);
            transition: all 0.3s ease;
        }
        
        /* Header styles */
        header {
            text-align: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .logo {
            width: 80px;
            height: 80px;
            margin-bottom: 1rem;
            display: flex;
            justify-content: center;
        }
        
        header h1 {
            font-size: 2.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: var(--text-muted);
            font-size: 1rem;
        }
        
        /* Section styles */
        section {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 4px 6px var(--shadow);
            margin-bottom: 2rem;
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
            overflow: hidden;
        }

        section > .section-header {
            padding: 1.25rem 2rem;
            background-color: var(--surface);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            border-bottom: 1px solid var(--border);
        }

        section > .section-header:hover {
            background-color: var(--surface-alt);
        }

        section > .section-content {
            max-height: 0;
            overflow: hidden;
            padding: 0 2rem;
            transition: all 0.3s ease;
            opacity: 0;
            border-top: 0;
        }

        section > .section-content.expanded {
            max-height: 2000px;
            overflow-y: visible;
            padding: 1.5rem 2rem;
            opacity: 1;
            border-top: 1px solid var(--border);
        }

        section > .section-header-static {
            padding: 1.25rem 2rem;
            background-color: var(--surface);
            border-bottom: 1px solid var(--border);
        }

        section > .section-content-static {
            padding: 1.5rem 2rem;
        }

        section h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }
        
        /* Stats container */
        .stats-container {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            flex: 1;
            min-width: 120px;
            background-color: var(--surface-alt);
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 4px var(--shadow);
            transition: transform 0.2s ease-in-out, background-color 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card.highlight {
            background-color: var(--primary-bg);
            border-left: 4px solid var(--primary);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Metrics container */
        .metrics-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .metric {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .metric-label {
            width: 120px;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        .progress-bar {
            flex: 1;
            height: 10px;
            background-color: var(--surface-alt);
            border-radius: 5px;
            overflow: hidden;
        }
        
        .progress {
            height: 100%;
            background-color: var(--primary-light);
            border-radius: 5px;
            transition: width 0.3s ease;
        }
        
        .metric-value {
            width: 60px;
            text-align: right;
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--primary-dark);
        }
        
        /* Config section */
        .config-details {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .config-item {
            padding: 0.75rem;
            border-radius: 6px;
            background-color: var(--surface-alt);
            transition: background-color 0.3s ease;
        }
        
        .config-label {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-right: 0.5rem;
        }
        
        .config-value {
            font-size: 0.875rem;
            color: var(--text-primary);
        }
        
        /* Prompts section */
        .filters {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 0.5rem 1rem;
            border: none;
            background-color: var(--surface-alt);
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .filter-btn:hover {
            background-color: var(--border);
        }
        
        .filter-btn.active {
            background-color: var(--primary);
            color: white;
        }
        
        .prompts-container {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .prompt-card {
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 2px 4px var(--shadow);
            overflow: hidden;
            border: 1px solid var(--border);
            transition: box-shadow 0.2s ease, background-color 0.3s ease;
        }
        
        .prompt-card:hover {
            box-shadow: 0 4px 8px var(--shadow-hover);
        }
        
        .prompt-card.anomaly {
            border-left: 4px solid var(--anomaly);
        }
        
        .prompt-card.refusal {
            border-left: 4px solid var(--refusal);
        }
        
        .prompt-card.mutation {
            border-left: 4px solid var(--mutation);
        }
        
        .prompt-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background-color: var(--surface-alt);
            border-bottom: 1px solid var(--border);
            transition: background-color 0.3s ease;
        }
        
        .prompt-index {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        .prompt-badges {
            display: flex;
            gap: 0.5rem;
        }
        
        .badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .anomaly-badge {
            background-color: var(--anomaly-bg);
            color: var(--anomaly-text);
        }
        
        .refusal-badge {
            background-color: var(--refusal-bg);
            color: var(--refusal-text);
        }
        
        .mutation-badge {
            background-color: var(--mutation-bg);
            color: var(--mutation-text);
        }
        
        .prompt-content {
            padding: 1rem;
        }
        
        .prompt-pair {
            margin-bottom: 1rem;
        }
        
        .prompt-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }
        
        .prompt-text {
            font-size: 0.875rem;
            color: var(--text-primary);
            padding: 0.5rem;
            background-color: var(--surface-alt);
            border-radius: 4px;
            word-break: break-word;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        .response-preview {
            max-height: 100px;
            overflow: hidden;
        }
        
        .expand-btn {
            width: 100%;
            padding: 0.75rem;
            background-color: var(--surface-alt);
            border: none;
            border-top: 1px solid var(--border);
            font-size: 0.875rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: background-color 0.2s ease, color 0.3s ease;
        }
        
        .expand-btn:hover {
            background-color: var(--border);
        }
        
        .full-response {
            padding: 1rem;
            background-color: var(--code-bg);
            max-height: 600px;
            overflow-y: auto;
            transition: background-color 0.3s ease;
        }
        
        .full-response pre {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
            font-size: 0.875rem;
            line-height: 1.5;
            color: var(--code-text);
            white-space: pre-wrap;
            word-break: break-word;
        }
        
        .hidden {
            display: none;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }

            .stats-container {
                flex-direction: column;
            }

            .stat-card {
                min-width: 100%;
            }

            .config-details {
                grid-template-columns: 1fr;
            }

            .metric {
                flex-direction: column;
                align-items: flex-start;
            }

            .metric-label, .metric-value {
                width: 100%;
                text-align: left;
            }
        }

        /* Table styling */
        .table-container {
            overflow-x: auto;
            margin-bottom: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px var(--shadow);
        }

        /* Reset table styles */
        table, tr, th, td {
            box-sizing: border-box !important;
        }

        .results-table {
            width: 100%;
            table-layout: fixed !important;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.875rem;
            background-color: var(--surface);
            border: 1px solid var(--border);
        }

        .results-table thead {
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .results-table th {
            background-color: var(--surface-alt);
            color: var(--text-primary);
            font-weight: 600;
            text-align: left;
            padding: 0.75rem 1rem;
            border-bottom: 2px solid var(--border);
            white-space: nowrap;
        }

        .results-table th:first-child {
            text-align: center;
            width: 50px;
        }

        .results-table th:nth-child(2) {
            width: 90px;
        }

        .results-table th:nth-child(3),
        .results-table th:nth-child(4),
        .results-table th:nth-child(5) {
            width: calc((100% - 200px) / 3);
        }

        .results-table th:last-child {
            width: 60px;
            text-align: center;
        }

        .results-table th.sortable {
            cursor: pointer;
            position: relative;
        }

        .results-table th.sortable:hover {
            background-color: var(--border);
        }

        .results-table th.sortable::after {
            content: '⇅';
            font-size: 0.75rem;
            margin-left: 0.5rem;
            opacity: 0.5;
        }

        .results-table td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }

        .results-table .index-cell {
            font-weight: 600;
            text-align: center;
            width: 50px;
        }

        .results-table .badge-cell {
            width: 90px;
            white-space: nowrap;
        }

        .results-table .text-cell {
            overflow: hidden;
            word-wrap: break-word;
            white-space: normal;
            line-height: 1.4;
            max-height: 4.2em;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            text-overflow: ellipsis;
            text-align: left;
            vertical-align: top;
            padding-top: 1rem;
        }

        .results-table .original-cell,
        .results-table .mutated-cell,
        .results-table .response-cell {
            box-sizing: border-box;
        }

        .results-table .action-cell {
            width: 60px;
            text-align: center;
        }

        .view-btn {
            padding: 0.35rem 0.75rem;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.75rem;
            font-weight: 500;
            transition: background-color 0.2s;
        }

        .view-btn:hover {
            background-color: var(--primary-dark);
        }

        .results-table tr:hover {
            background-color: var(--surface-alt);
        }

        .results-table tr.anomaly {
            border-left: 3px solid var(--anomaly);
        }

        .results-table tr.refusal {
            border-left: 3px solid var(--refusal);
        }

        .results-table tr.mutation {
            border-left: 3px solid var(--mutation);
        }

        .results-table tr.normal {
            border-left: 3px solid transparent;
        }

        /* Modal section styling for collapsible content */
        .modal-section {
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            overflow: hidden;
        }

        .modal-section .section-content {
            max-height: 0;
            overflow: hidden;
            padding: 0 1rem;
            transition: all 0.3s ease;
            opacity: 0;
        }

        .modal-section .section-content.expanded {
            max-height: 600px;
            overflow-y: auto;
            padding: 1rem;
            opacity: 1;
        }

        .section-header {
            padding: 0.75rem 1rem;
            background-color: var(--surface-alt);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
        }

        .section-header:hover {
            background-color: var(--border);
        }

        .section-header h4 {
            font-size: 1rem;
            color: var(--text-secondary);
            font-weight: 600;
            margin: 0;
        }

        .section-toggle {
            color: var(--text-secondary);
            font-size: 0.75rem;
            transition: transform 0.3s ease;
        }

        .section-toggle.collapsed {
            transform: rotate(-90deg);
        }

        .section-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }

        .section-content.expanded {
            max-height: 600px;
            overflow-y: auto;
            padding: 1rem;
        }

        .normal-badge {
            background-color: var(--normal-bg);
            color: var(--normal-text);
        }
        """


def generate_report(results_dir: Path, output_path: Optional[Path] = None) -> Path:
    """
    Generate an HTML report from fuzzing results.

    Args:
        results_dir: Path to the directory containing fuzzing results
        output_path: Path to save the HTML report to
                     If None, saves to results_dir/report.html

    Returns:
        Path to the generated HTML report
    """
    generator = ReportGenerator(results_dir)
    return generator.generate_html_report(output_path)
