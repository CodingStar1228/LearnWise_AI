// 难度：数字(1-5)或中文 -> {label, cls}
function formatDifficulty(d) {
    if (typeof d === 'number') {
        if (d <= 2) return { label: '简单', cls: 'easy' };
        if (d >= 4) return { label: '困难', cls: 'hard' };
        return { label: '中等', cls: 'medium' };
    }
    if (d === '简单') return { label: '简单', cls: 'easy' };
    if (d === '困难') return { label: '困难', cls: 'hard' };
    return { label: d || '中等', cls: 'medium' };
}

// 题型英文 -> 中文展示
function formatType(t) {
    const map = {
        'concept': '概念题',
        'calculation': '计算题',
        'application': '应用题',
        'multiple-choice': '选择题',
        'mcq': '选择题',
    };
    return map[t] || t || '题目';
}

document.addEventListener('DOMContentLoaded', function() {
    // 存储数据
    let chapters = [];
    let currentChapter = null;
    let currentSubject = '';
    let subjects = [];
    
    // 获取DOM元素
    const subjectSelect = document.getElementById('subject-select');
    const chapterList = document.getElementById('chapter-list');
    const questionList = document.getElementById('question-list');
    const currentChapterTitle = document.getElementById('current-chapter-title');
    
    // 配置marked选项
    marked.use({
        breaks: true,  // 允许在换行时添加<br>标签
        gfm: true      // 使用GitHub风格的Markdown
    });
    
    // 初始化
    init();
    
    async function init() {
        try {
            // 加载科目列表
            await loadSubjects();
            // 加载章节数据
            await loadChapters();
        } catch (error) {
            console.error('初始化失败:', error);
            questionList.innerHTML = '<p class="empty-tip">加载失败，请刷新页面重试</p>';
        }
    }
    
    // 加载科目列表
    async function loadSubjects() {
        try {
            const response = await fetch('/api/subjects');
            if (!response.ok) {
                throw new Error('获取科目数据失败');
            }
            
            const data = await response.json();
            // /api/subjects 返回的是数组；兼容旧的 {subjects:[...]} 形式
            subjects = Array.isArray(data) ? data : (data.subjects || []);
            
            // 填充科目选择器
            subjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject.id;
                option.textContent = subject.name;
                subjectSelect.appendChild(option);
            });
            
            // 监听科目变化
            subjectSelect.addEventListener('change', (e) => {
                currentSubject = e.target.value;
                loadChapters();
            });
        } catch (error) {
            console.error('加载科目失败:', error);
        }
    }
    
    // 加载章节列表
    async function loadChapters() {
        try {
            chapterList.innerHTML = '<li class="empty-tip">加载中...</li>';
            
            let url = '/api/chapters';
            if (currentSubject) {
                url += `?subject=${currentSubject}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('获取章节数据失败');
            }
            
            chapters = await response.json();
            renderChapters();
        } catch (error) {
            console.error('加载章节失败:', error);
            chapterList.innerHTML = '<li class="empty-tip">加载章节失败，请刷新重试</li>';
        }
    }
    
    // 渲染章节列表
    function renderChapters() {
        chapterList.innerHTML = '';
        
        chapters.forEach((chapter, idx) => {
            const li = document.createElement('li');
            li.className = 'chapter-item';
            li.dataset.id = chapter.id;
            li.textContent = `${idx + 1}. ${chapter.title}`;
            
            li.addEventListener('click', () => selectChapter(chapter));
            
            chapterList.appendChild(li);
        });
        
        // 默认选中第一个章节
        if (chapters.length > 0) {
            selectChapter(chapters[0]);
        }
    }
    
    // 选择章节
    function selectChapter(chapter) {
        currentChapter = chapter;
        
        // 更新UI
        const chapterItems = document.querySelectorAll('.chapter-item');
        chapterItems.forEach(item => {
            if (item.dataset.id === chapter.id) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // 更新标题
        currentChapterTitle.textContent = ` - ${chapter.title}`;
        
        // 加载问题
        loadQuestions(chapter.id);
    }
    
    // 加载问题列表
    async function loadQuestions(chapterId) {
        try {
            questionList.innerHTML = '<p class="empty-tip">加载中...</p>';
            
            const response = await fetch(`/api/chapters/${chapterId}/questions`);
            if (!response.ok) {
                throw new Error('获取题目数据失败');
            }
            
            const questions = await response.json();
            renderQuestions(questions);
        } catch (error) {
            console.error('加载题目失败:', error);
            questionList.innerHTML = '<p class="empty-tip">加载题目失败，请重试</p>';
        }
    }
    
    // 渲染问题列表
    function renderQuestions(questions) {
        if (!questions || questions.length === 0) {
            questionList.innerHTML = '<p class="empty-tip">该章节暂无题目</p>';
            return;
        }
        
        questionList.innerHTML = '';
        
        questions.forEach(question => {
            const div = document.createElement('div');
            div.className = 'question-item';
            
            // 难度：支持数字(1-5)或中文字符串，统一映射为 易/中/难
            const { label: difficultyLabel, cls: difficultyClass } = formatDifficulty(question.difficulty);
            const typeLabel = formatType(question.type);
            
            // 使用Markdown渲染标题
            const titleHTML = marked.parse(question.title || '');
            // 去除<p>标签以保持样式一致性
            const formattedTitle = titleHTML.replace(/<\/?p>/g, '');
            
            div.innerHTML = `
                <div class="title">${formattedTitle}</div>
                <div class="meta">
                    <span>${typeLabel}</span>
                    <span class="difficulty ${difficultyClass}">${difficultyLabel}</span>
                </div>
            `;
            
            // 点击跳转到问题详情页
            div.addEventListener('click', () => {
                window.location.href = `/chat/${question.id}`;
            });
            
            questionList.appendChild(div);
        });
    }
}); 