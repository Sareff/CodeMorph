// static/js/diagram.js

// 1. Инициализация Mermaid.js с учётом securityLevel
mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    flowchart: { htmlLabels: true },
    class: { useMaxWidth: true }
});

// 2. Генерация диаграммы Mermaid на основе данных
function generateMermaidDiagram(data) {
    let diagram = 'classDiagram\n\n';

    // Создаём словарь для быстрого доступа к классам по их имени
    let classMap = {};
    data.classes.forEach((cls, index) => {
        classMap[cls.name] = cls;
    });

    // Массив для хранения уже добавленных имён классов, чтобы избежать дублирования
    let addedClasses = new Set();

    // Функция для добавления класса в диаграмму
    function addClassToDiagram(cls) {
        if (addedClasses.has(cls.name)) {
            return;
        }
        addedClasses.add(cls.name);

        let classId = `Class_${cls.name.replace(/\W/g, '_')}`;
        cls.id = classId;

        diagram += `class ${classId}["${cls.name}"] {\n`;

        // Обрабатываем атрибуты
        (cls.attributes || []).forEach(attr => {
            const processedAttr = attr.replace(/^([+#-])\s+/, '$1').replace(':', ' ');
            diagram += `  ${processedAttr}\n`;
        });

        // Обрабатываем методы
        (cls.methods || []).forEach(method => {
            const processedMethod = method.replace(/^([+#-])\s+/, '$1').replace(':', ' ');
            diagram += `  ${processedMethod}\n`;
        });

        if (cls.methods.length === 0 && cls.attributes.length === 0) {
            diagram += `  + Empty class`
        }

        diagram += '}\n\n';

        // Добавляем директиву клика для класса
        diagram += `click ${classId} call openClassPage(${cls.name}) "${cls.name}"\n\n`;
    }

    // Добавляем все классы из данных
    data.classes.forEach(cls => {
        addClassToDiagram(cls);
    });

    // Обрабатываем отношения
    data.relationships.forEach(rel => {
        let fromClass = classMap[rel.from];
        let toClass = classMap[rel.to];

        // Если базовый класс не найден, создаём его как абстрактный класс
        if (!toClass) {
            toClass = {
                name: rel.to,
                attributes: ["+ this is imported class"],
                methods: [],
                info: '',
                isAbstract: true
            };
            classMap[rel.to] = toClass;
            addClassToDiagram(toClass);
        }

        // Если производный класс не добавлен в диаграмму, добавляем его
        if (!fromClass) {
            fromClass = {
                name: rel.from,
                attributes: ["+ this is fromClass"],
                methods: [],
                info: ''
            };
            classMap[rel.from] = fromClass;
            addClassToDiagram(fromClass);
        }

        let relationSymbol = '-->';
        if (rel.type === 'inheritance') {
            relationSymbol = '<|--';
        } else if (rel.type === 'association') {
            relationSymbol = '--';
        }

        diagram += `${toClass.id} ${relationSymbol} ${fromClass.id}\n`;
    });

    return diagram;
}

// 3. Функция для открытия страницы класса
window.openClassPage = function(className) {
    // Перенаправляем пользователя на страницу класса
    window.location.href = `/class/${className}`;
};

// 4. Рендеринг диаграммы
(async function() {
    var diagramDefinition = generateMermaidDiagram(classesData);

    console.log('Diagram Definition:\n', diagramDefinition); // Для отладки

    try {
        const { svg, bindFunctions } = await mermaid.render('generatedDiagram', diagramDefinition);

        // Удаляем стиль 'max-width' из SVG
        const cleanedSvg = svg.replace(/(\s)*max-width:(\s)*(\d+\.?\d*)px;/gi, '');

        document.getElementById('uml-diagram').innerHTML = cleanedSvg;

        if (bindFunctions) {
            bindFunctions(document.getElementById('uml-diagram'));
        }

        // Инициализируем svg-pan-zoom
        initPanZoom();
    } catch (err) {
        console.error('Ошибка при рендеринге диаграммы:', err);
    }
})();

// 5. Функция для инициализации svg-pan-zoom
function initPanZoom() {
    var svgElement = document.querySelector('#uml-diagram svg');
    if (!svgElement) {
        console.error('SVG не найден для панорамирования и масштабирования.');
        return;
    }

    // Инициализируем svg-pan-zoom
    svgPanZoom(svgElement, {
        zoomEnabled: true,
        controlIconsEnabled: true,
        fit: true,
        center: true
    });
}