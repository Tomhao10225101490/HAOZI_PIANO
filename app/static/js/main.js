document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            alert('请输入搜索关键词');
            return;
        }

        try {
            resultsContainer.innerHTML = '<p>搜索中...</p>';
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.error) {
                resultsContainer.innerHTML = `<p class="error">${data.error}</p>`;
                return;
            }

            if (data.results.length === 0) {
                resultsContainer.innerHTML = '<p>未找到相关乐谱，请尝试其他关键词</p>';
                return;
            }

            displayResults(data.results);
        } catch (error) {
            resultsContainer.innerHTML = '<p class="error">搜索出错，请稍后重试</p>';
        }
    }

    function displayResults(results) {
        resultsContainer.innerHTML = results.map(sheet => `
            <div class="sheet-card">
                <h3>${sheet.title}</h3>
                ${sheet.composer ? `<p>作曲家：${sheet.composer}</p>` : ''}
                <img src="${sheet.preview_url}" alt="${sheet.title}">
                <p>共 ${sheet.page_count} 页</p>
                <div class="download-buttons">
                    ${sheet.download_urls.map((url, index) => `
                        <a href="/api/download/${encodeURIComponent(url)}" 
                           class="download-btn" 
                           download>
                            下载第${index + 1}页
                        </a>
                    `).join('')}
                    <a href="/api/download_pdf/${encodeURIComponent(sheet.detail_url)}"
                       class="download-btn pdf-btn"
                       download>
                        下载PDF版本
                    </a>
                </div>
            </div>
        `).join('');
    }
}); 