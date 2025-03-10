document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event triggered.');

    const conferenceTableBody = document.getElementById('conference-table-body');
    const rankingTableBody = document.querySelector('#ranking-table tbody');
    const relatedConferencesButton = document.getElementById('related-conferences');
    const readMeButton = document.getElementById('read-me');

    // Related Conferences 按钮跳转
    if (relatedConferencesButton) {
        relatedConferencesButton.addEventListener('click', () => {
            window.location.href = '/related-conferences';
        });
    }

    // Read ME 按钮跳转
    if (readMeButton) {
        readMeButton.addEventListener('click', () => {
            window.location.href = '/read-me';
        });
    }

    if (conferenceTableBody) {
        console.log('Related Conferences page detected. Loading conferences...');
        loadConferences();
        return;
    }

    if (rankingTableBody) {
        console.log('Main page detected. Loading university rankings...');
        loadUniversityRankings();
        return;
    }

    console.error('Unable to detect page type. Check your HTML structure.');
});

// 加载 Related Conferences 数据
function loadConferences() {
    fetch('/static/rankings/data/conferences.json')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            const conferenceTableBody = document.getElementById('conference-table-body');
            if (!conferenceTableBody) {
                console.error('conference-table-body not found in the DOM.');
                return;
            }
            conferenceTableBody.innerHTML = data.map((conf, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td>${conf.name}</td>
                </tr>
            `).join('');
        })
        .catch(error => console.error('Error loading conferences:', error));
}

// 加载大学排名数据
function loadUniversityRankings() {
    const rankingTableBody = document.querySelector('#ranking-table tbody');
    const paginationDiv = document.getElementById('pagination');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    let universities = [];
    let filteredUniversities = [];
    const itemsPerPage = 20;
    let currentPage = 1;

    fetch('/static/rankings/data/universities_score.json')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            universities = data.map((u, index) => ({
                rank: index + 1,
                university: u.university_name,
                score: parseFloat(u.total_score)
            }));
            renderPage(currentPage, universities);
            renderPagination(universities);
        })
        .catch(error => console.error('Error loading universities JSON:', error));

    if (searchButton) {
        searchButton.addEventListener('click', () => {
            const query = searchInput.value
                .trim()
                .replace(/[^a-zA-Z0-9一-龥]/g, '') // 保留字母、数字和中文
                .toLowerCase();

            if (!query) {
                alert('请输入有效的搜索内容！');
                return;
            }

            let sourceData = filteredUniversities && filteredUniversities.length > 0
                ? filteredUniversities
                : universities;

            filteredUniversities = sourceData.filter(u =>
                u.university
                    .replace(/[^a-zA-Z0-9一-龥]/g, '')
                    .toLowerCase()
                    .includes(query)
            );

            if (filteredUniversities.length === 0) {
                alert('未找到匹配的结果，请尝试其他搜索关键词。');
                return;
            }

            currentPage = 1;
            renderPage(currentPage, filteredUniversities);
            renderPagination(filteredUniversities);
        });
    }

    function renderPage(page, dataSource = universities) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageData = dataSource.slice(start, end);

        rankingTableBody.innerHTML = pageData.map(row => `
            <tr class="university-row" data-university="${row.university}" data-rank="${row.rank}">
                <td>${row.rank}</td>
                <td>${row.university}</td>
                <td>${row.score.toFixed(2)}</td>
            </tr>
            <tr class="collapsible" data-university="${row.university}">
                <td colspan="3" class="collapsible-content"></td>
            </tr>
        `).join('');
    }

    function renderPagination(dataSource = universities) {
        const totalPages = Math.ceil(dataSource.length / itemsPerPage);
        const maxVisiblePages = 10;
        const startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        paginationDiv.innerHTML = '';

        if (currentPage > 1) {
            const prevButton = document.createElement('button');
            prevButton.textContent = '«';
            prevButton.addEventListener('click', () => {
                currentPage--;
                renderPage(currentPage, dataSource);
                renderPagination(dataSource);
            });
            paginationDiv.appendChild(prevButton);
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.disabled = i === currentPage;
            pageButton.addEventListener('click', () => {
                currentPage = i;
                renderPage(currentPage, dataSource);
                renderPagination(dataSource);
            });
            paginationDiv.appendChild(pageButton);
        }

        if (currentPage < totalPages) {
            const nextButton = document.createElement('button');
            nextButton.textContent = '»';
            nextButton.addEventListener('click', () => {
                currentPage++;
                renderPage(currentPage, dataSource);
                renderPagination(dataSource);
            });
            paginationDiv.appendChild(nextButton);
        }
    }

    document.addEventListener('click', (event) => {
        const universityRow = event.target.closest('.university-row');
        if (universityRow) {
            const universityName = universityRow.dataset.university;
            toggleAuthors(universityName);
        }

        const authorRow = event.target.closest('.author-row');
        if (authorRow) {
            const authorName = authorRow.dataset.author;
            togglePapers(authorRow, authorName);
        }
    });

    function toggleAuthors(universityName) {
        const collapsibleRow = document.querySelector(`.collapsible[data-university="${universityName}"]`);
        if (!collapsibleRow) return;

        if (collapsibleRow.classList.contains('open')) {
            collapsibleRow.classList.remove('open');
            collapsibleRow.style.minHeight = '1px'; // 保留最小高度，防止布局塌陷
            collapsibleRow.innerHTML = ''; // 清空内容
        } else {
            loadAuthors(universityName, collapsibleRow);
        }
    }

    function loadAuthors(universityName, collapsibleRow) {
        fetch('/static/rankings/data/university_author_score.json')
            .then(response => response.json())
            .then(data => {
                const universityData = data.find(u => u.university_name === universityName);
                if (universityData) {
                    collapsibleRow.innerHTML = `
                        <td colspan="3">
                            <table class="nested-table">
                                <thead>
                                    <tr>
                                        <th>Author</th>
                                        <th>Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${universityData.authors.map(author => `
                                        <tr class="author-row" data-author="${author.name}">
                                            <td>${author.name}</td>
                                            <td>${author.score.toFixed(1)}</td>
                                        </tr>
                                        <tr class="paper-collapsible" id="papers-${author.name}">
                                            <td colspan="2" class="collapsible-content"></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </td>
                    `;
                    collapsibleRow.style.height = 'auto'; // 动态调整高度
                    collapsibleRow.classList.add('open');
                }
            })
            .catch(error => console.error('Error loading authors:', error));
    }

    function togglePapers(authorRow, authorName) {
        const paperRow = authorRow.nextElementSibling;
        if (!paperRow) return;

        if (paperRow.classList.contains('open')) {
            paperRow.classList.remove('open');
            paperRow.innerHTML = ''; // 清空内容
        } else {
            paperRow.classList.add('open');
            fetch('/static/rankings/data/authors_papers.json')
                .then(response => response.json())
                .then(data => {
                    const authorData = data.find(a => a.author_name === authorName);
                    if (authorData) {
                        // 确保 `papers` 是数组，并正确渲染为 `<ul><li>`
                        const papersList = Array.isArray(authorData.papers)
                            ? authorData.papers.map(paper => `<li>${paper}</li>`).join('')
                            : `<li>${authorData.papers}</li>`;  // 防止 `papers` 仍然是字符串

                        paperRow.innerHTML = `
                            <td colspan="2">
                                <ul class="papers-list">
                                    ${papersList}
                                </ul>
                            </td>
                        `;
                        paperRow.style.minHeight = 'auto'; // 动态适配内容高度
                    }
                })
                .catch(error => console.error('Error loading papers:', error));
        }
    }
}
