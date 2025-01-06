document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event triggered.');

    // 判断当前页面类型，根据页面加载对应的逻辑
    const conferenceTableBody = document.getElementById('conference-table-body');
    const rankingTableBody = document.querySelector('#ranking-table tbody');

    // 如果是 Related Conferences 页面
    if (conferenceTableBody) {
        console.log('Related Conferences page detected. Loading conferences...');
        loadConferences();
        return;
    }

    // 如果是主页面
    if (rankingTableBody) {
        console.log('Main page detected. Loading university rankings...');
        loadUniversityRankings();
        return;
    }

    console.error('Unable to detect page type. Check your HTML structure.');
});

// 加载 Related Conferences 数据
function loadConferences() {
    console.log('Attempting to load conferences...');
    fetch('/static/rankings/data/conferences.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
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
    const relatedConferencesButton = document.getElementById('related-conferences');
    const readMeButton = document.getElementById('read-me');

    if (!rankingTableBody || !paginationDiv || !searchInput || !searchButton || !relatedConferencesButton || !readMeButton) {
        console.error('Required elements not found in the DOM. Check HTML structure.');
        return;
    }

    let universities = [];
    const itemsPerPage = 20;
    let currentPage = 1;

    fetch('/static/rankings/data/universities_score.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            universities = data.map((u, index) => ({
                rank: index + 1,
                university: u.university_name,
                score: parseFloat(u.total_score)
            }));
            renderPage(currentPage);
            renderPagination();
        })
        .catch(error => console.error('Error loading universities JSON:', error));

    // 渲染当前页数据
    function renderPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageData = universities.slice(start, end);

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

    // 渲染分页控件
    function renderPagination() {
        const totalPages = Math.ceil(universities.length / itemsPerPage);
        paginationDiv.innerHTML = '';

        for (let i = 1; i <= totalPages; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.disabled = i === currentPage;
            pageButton.addEventListener('click', () => {
                currentPage = i;
                renderPage(currentPage);
                renderPagination();
            });
            paginationDiv.appendChild(pageButton);
        }
    }

    // 搜索功能
    function performSearch() {
        const query = searchInput.value.toLowerCase().replace(/[^a-z0-9]/gi, '');
        const filteredUniversities = universities.filter(u =>
            u.university.toLowerCase().includes(query)
        );

        rankingTableBody.innerHTML = filteredUniversities.map(row => `
            <tr class="university-row" data-university="${row.university}" data-rank="${row.rank}">
                <td>${row.rank}</td>
                <td>${row.university}</td>
                <td>${row.score.toFixed(2)}</td>
            </tr>
            <tr class="collapsible" data-university="${row.university}">
                <td colspan="3" class="collapsible-content"></td>
            </tr>
        `).join('');
        paginationDiv.innerHTML = ''; // 清空分页控件
    }

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            performSearch();
        }
    });

    // Related Conferences 和 Read ME 页面按钮功能
    relatedConferencesButton?.addEventListener('click', () => {
        window.location.href = '/related-conferences';
    });

    readMeButton?.addEventListener('click', () => {
        window.location.href = '/read-me';
    });

    // 切换作者列表展开/收起逻辑
    document.addEventListener('click', (event) => {
        const universityRow = event.target.closest('.university-row');
        if (universityRow) {
            const universityName = universityRow.dataset.university;
            toggleAuthors(universityName);
        }

        const authorRow = event.target.closest('.author-row');
        if (authorRow) {
            const authorName = authorRow.dataset.author;
            loadPapers(authorName);
        }
    });

    function toggleAuthors(universityName) {
        const collapsibleRow = document.querySelector(`.collapsible[data-university="${universityName}"]`);
        if (collapsibleRow) {
            if (collapsibleRow.classList.contains('open')) {
                collapsibleRow.classList.remove('open');
                collapsibleRow.innerHTML = '';
            } else {
                loadAuthors(universityName, collapsibleRow);
            }
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
                                    `).join('')}
                                </tbody>
                            </table>
                        </td>
                    `;
                    collapsibleRow.classList.add('open');
                }
            })
            .catch(error => console.error('Error loading authors:', error));
    }

    function loadPapers(authorName) {
        fetch('/static/rankings/data/authors_papers.json')
            .then(response => response.json())
            .then(data => {
                const authorData = data.find(a => a.author_name === authorName);
                if (authorData) {
                    alert(`Papers by ${authorName}:\n${authorData.papers.join('\n')}`);
                } else {
                    alert(`No papers found for author: ${authorName}`);
                }
            })
            .catch(error => console.error('Error loading papers:', error));
    }
}









document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event triggered.');

    // 获取页面元素
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

    // 如果是 Related Conferences 页面
    if (conferenceTableBody) {
        console.log('Related Conferences page detected. Loading conferences...');
        loadConferences();
        return;
    }

    // 如果是大学排名主页面
    if (rankingTableBody) {
        console.log('Main page detected. Loading university rankings...');
        loadUniversityRankings();
        return;
    }

    console.error('Unable to detect page type. Check your HTML structure.');
});

// 加载 Related Conferences 数据
function loadConferences() {
    console.log('Attempting to load conferences...');
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
            renderPage(currentPage);
            renderPagination();
        })
        .catch(error => console.error('Error loading universities JSON:', error));

    function renderPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageData = universities.slice(start, end);

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

    function renderPagination() {
        const totalPages = Math.ceil(universities.length / itemsPerPage);
        paginationDiv.innerHTML = '';

        for (let i = 1; i <= totalPages; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.disabled = i === currentPage;
            pageButton.addEventListener('click', () => {
                currentPage = i;
                renderPage(currentPage);
                renderPagination();
            });
            paginationDiv.appendChild(pageButton);
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
            collapsibleRow.innerHTML = '';
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
            paperRow.innerHTML = '';
        } else {
            paperRow.classList.add('open');
            fetch('/static/rankings/data/authors_papers.json')
                .then(response => response.json())
                .then(data => {
                    const authorData = data.find(a => a.author_name === authorName);
                    if (authorData) {
                        paperRow.innerHTML = `
                            <td colspan="2">
                                <ul>
                                    ${authorData.papers.map(paper => `<li>${paper}</li>`).join('')}
                                </ul>
                            </td>
                        `;
                    }
                })
                .catch(error => console.error('Error loading papers:', error));
        }
    }
}



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
            renderPage(currentPage);
            renderPagination();
        })
        .catch(error => console.error('Error loading universities JSON:', error));

    if (searchButton) {
        searchButton.addEventListener('click', () => {
            const query = searchInput.value.trim().toLowerCase();
            const filteredUniversities = universities.filter(u =>
                u.university.toLowerCase().includes(query)
            );
            universities = filteredUniversities;
            currentPage = 1; // 重置到第一页
            renderPage(currentPage);
            renderPagination();
        });
    }

    function renderPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageData = universities.slice(start, end);

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

    function renderPagination() {
        const totalPages = Math.ceil(universities.length / itemsPerPage);
        const maxVisiblePages = 10;
        const startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        paginationDiv.innerHTML = '';

        if (currentPage > 1) {
            const prevButton = document.createElement('button');
            prevButton.textContent = '«';
            prevButton.addEventListener('click', () => {
                currentPage--;
                renderPage(currentPage);
                renderPagination();
            });
            paginationDiv.appendChild(prevButton);
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.disabled = i === currentPage;
            pageButton.addEventListener('click', () => {
                currentPage = i;
                renderPage(currentPage);
                renderPagination();
            });
            paginationDiv.appendChild(pageButton);
        }

        if (currentPage < totalPages) {
            const nextButton = document.createElement('button');
            nextButton.textContent = '»';
            nextButton.addEventListener('click', () => {
                currentPage++;
                renderPage(currentPage);
                renderPagination();
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
            paperRow.style.minHeight = '1px'; // 保留最小高度，防止布局塌陷
            paperRow.innerHTML = ''; // 清空内容
        } else {
            paperRow.classList.add('open');
            fetch('/static/rankings/data/authors_papers.json')
                .then(response => response.json())
                .then(data => {
                    const authorData = data.find(a => a.author_name === authorName);
                    if (authorData) {
                        paperRow.innerHTML = `
                            <td colspan="2">
                                <ul>
                                    ${authorData.papers.map(paper => `<li>${paper}</li>`).join('')}
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
