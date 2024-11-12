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

    data.classes.forEach((cls, index) => {
        let classId = `Class${index}`;
        cls.id = classId;

        diagram += `class ${classId}["${cls.name}"] {\n`;

        // Обрабатываем атрибуты
        cls.attributes.forEach(attr => {
            // Удаляем пробел после символа видимости и корректируем синтаксис
            const processedAttr = attr.replace(/^([+#-])\s+/, '$1').replace(':', ' ');
            diagram += `  ${processedAttr}\n`;
        });

        // Обрабатываем методы
        cls.methods.forEach(method => {
            // Удаляем пробел после символа видимости и корректируем синтаксис
            const processedMethod = method.replace(/^([+#-])\s+/, '$1').replace(':', ' ');
            diagram += `  ${processedMethod}\n`;
        });

        diagram += '}\n\n';

        // Добавляем директиву клика для класса
        diagram += `click ${classId} call openClassPage(${cls.name}) "${cls.name}"\n\n`;
    });

    // Определяем отношения
    data.relationships.forEach(rel => {
        let fromClass = data.classes.find(cls => cls.name === rel.from);
        let toClass = data.classes.find(cls => cls.name === rel.to);

        let relationSymbol = '-->';
        if (rel.type === 'inheritance') {
            relationSymbol = '<|--';
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
        center: true,
        minZoom: 0.3,
        maxZoom: 2,
        zoomScaleSensitivity: 0.3,
        panEnabled: true
    });
}