# ==============================================================================
# COMPILADOR DE PORTAL AMAZONÍA - AVRORA SOFT VIBOLA LLC
# Base de Datos Completa sin Truncar y Sistema de Inyección Dinámica UTF-8
# ==============================================================================

$rutaPlantilla = "$PWD\plantilla_matriz.html"
if (-Not (Test-Path $rutaPlantilla)) {
    Write-Host "Error: No se encuentra plantilla_matriz.html en el directorio actual." -ForegroundColor Red
    Exit
}

$plantillaHTML = Get-Content $rutaPlantilla -Raw -Encoding UTF8
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

# ================= BASE DE DATOS COMPLETA E INDEPENDIENTE (36 ETNIAS) =================
$etnias = @(
    @{
        id = "afroboliviano"
        prefijo_foto = "afro"
        menu_nombre = "1. Afro"
        titulo = "Afro-Boliviano"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento de La Paz (Provincias Nor Yungas y Sud Yungas).</li><li><strong>Ecosistema:</strong> Valles subtropicales (Yungas).</li><li><strong>Familia Lingüística:</strong> Castellano con modismos propios.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Descendientes de africanos traídos durante la época colonial para trabajar en las minas de Potosí. Debido a la altitud extrema, fueron trasladados a los Yungas para trabajar en haciendas de coca y cítricos, donde fusionaron su cultura ancestral con traditions andinas.</p><h3>Organización Social y Economía</h3><p>Su economía se basa en el cultivo de cítricos, café y hoja de coca. Mantienen una fuerte identidad comunitaria impulsada por la danza y música de la Saya, y poseen la figura única del 'Rey Afroboliviano'.</p><h3>Situación Actual</h3><p>Reconocidos oficialmente por el Estado Plurinacional, luchan por la consolidación de sus derechos territoriales y la erradicación de barreras sistémicas.</p>"
        color_mapa = "#FFB81C"
        coords = "[[-16.3, -67.5], [-16.0, -67.5], [-16.0, -67.1], [-16.3, -67.1]]"
    },
    @{
        id = "araona"
        prefijo_foto = "araona"
        menu_nombre = "2. Araona"
        titulo = "Araona"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento de La Paz (Provincia Iturralde).</li><li><strong>Ecosistema:</strong> Selva amazónica.</li><li><strong>Familia Lingüística:</strong> Tacana.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Fueron diezmados durante la fiebre del caucho y forzados al aislamiento voluntario en la cuenca de los ríos Manupari para sobrevivir. Recién restablecieron contacto en la década de 1960.</p><h3>Organización Social y Economía</h3><p>Dependen de la selva para subsistir, combinando cacería, pesca, recolección de castaña amazónica y agricultura itinerante en pequeños chacos.</p><h3>Situación Actual</h3><p>Son altamente vulnerables por su reducido número demográfico. Sufren la presión constante de la tala ilegal y la invasión extractiva en su territorio.</p>"
        color_mapa = "#1D9A4C"
        coords = "[[-12.5, -67.8], [-12.1, -67.8], [-12.1, -67.2], [-12.5, -67.2]]"
    },
    @{
        id = "aymara"
        prefijo_foto = "aymara"
        menu_nombre = "3. Aymara"
        titulo = "Aymara"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> La Paz, Oruro y Potosí.</li><li><strong>Ecosistema:</strong> Altiplano y valles interandinos.</li><li><strong>Familia Lingüística:</strong> Aymara.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Herederos de los antiguos señoríos andinos post-Tiwanaku. Resistieron al Imperio Inca y al régimen colonial español, preservando celosamente sus estructuras sociales y lingüísticas a lo largo de los siglos.</p><h3>Organización Social y Economía</h3><p>Su estructura base es el Ayllu. Su economía tradicional, fundamentada en la agricultura de alta montaña (sobre los 3500 metros) y pastoreo de camélidos, se ha expandido al comercio global y manufactura en áreas urbanas.</p><h3>Situación Actual</h3><p>Tienen un inmenso peso político y demográfico en Bolivia. Enfrentan los desafíos modernos de la migración urbana y el severo cambio climático en el altiplano.</p>"
        color_mapa = "#8E44AD"
        coords = "[[-18.0, -69.0], [-15.5, -69.0], [-15.5, -67.5], [-18.0, -67.5]]"
    },
    @{
        id = "ayoreo"
        prefijo_foto = "ayoreo"
        menu_nombre = "4. Ayoreo"
        titulo = "Ayoreo"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Santa Cruz (Provincias Germán Busch y Chiquitos).</li><li><strong>Ecosistema:</strong> Chaco boliviano y bosque seco.</li><li><strong>Familia Lingüística:</strong> Zamuco.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Fueron cazadores-recolectores nómadas hasta su forzoso contacto y sedentarización a mediados del siglo XX por el avance del ferrocarril y las misiones, lo cual trajo consigo un choque epidemiológico devastador.</p><h3>Organización Social y Economía</h3><p>Pasaron del nomadismo a combinar la recolección, el trabajo asalariado y la elaboración de artesanías en zonas periurbanas y rurales.</p><h3>Situación Actual</h3><p>Experimentan marginación y una agresiva pérdida de su hábitat chaqueño. Existen documentados grupos de ayoreos en estado de aislamiento voluntario huyendo de la deforestación.</p>"
        color_mapa = "#D35400"
        coords = "[[-19.5, -61.5], [-17.5, -61.5], [-17.5, -59.0], [-19.5, -59.0]]"
    },
    @{
        id = "baure"
        prefijo_foto = "baure"
        menu_nombre = "5. Baure"
        titulo = "Baure"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (Provincia Iténez).</li><li><strong>Ecosistema:</strong> Sabanas inundables amazónicas.</li><li><strong>Familia Lingüística:</strong> Arawak.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Descendientes de la avanzada cultura prehispánica de Moxos, constructores de colosales obras hidráulicas. Fueron asimilados al sistema jesuita a finales del siglo XVII.</p><h3>Organización Social y Economía</h3><p>Son célebres por su manejo y procesamiento artesanal del cacao silvestre. La agricultura y la cacería complementan su dieta. Se rigen por el tradicional Cabildo Indigenal.</p><h3>Situación Actual</h3><p>Buscan certificar el cacao como un motor económico sostenible mientras enfrentan la pérdida de su idioma materno y la expansión de la frontera ganadera.</p>"
        color_mapa = "#2980B9"
        coords = "[[-13.8, -64.5], [-13.2, -64.5], [-13.2, -63.8], [-13.8, -63.8]]"
    },
    @{
        id = "canichana"
        prefijo_foto = "canichana"
        menu_nombre = "6. Canichana"
        titulo = "Canichana"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (San Javier).</li><li><strong>Ecosistema:</strong> Sabanas y llanuras.</li><li><strong>Familia Lingüística:</strong> Aislada.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Pueblo guerrero de los Llanos de Moxos. Fueron severamente diezmados en la época republicana al ser forzados a trabajar en las siringas de goma y expediciones fluviales.</p><h3>Organización Social y Economía</h3><p>Integrados al sistema laboral de estancias ganaderas. Su economía combina agricultura de subsistencia con trabajo jornalero.</p><h3>Situación Actual</h3><p>Con su idioma nativo considerado extinto, enfrentan una constante lucha por consolidar tierras ante invasiones ganaderas.</p>"
        color_mapa = "#E74C3C"
        coords = "[[-14.5, -64.9], [-14.0, -64.9], [-14.0, -64.2], [-14.5, -64.2]]"
    },
    @{
        id = "cavineno"
        prefijo_foto = "cavineno"
        menu_nombre = "7. Cavineño"
        titulo = "Cavineño"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Beni y Pando.</li><li><strong>Ecosistema:</strong> Selva amazónica.</li><li><strong>Familia Lingüística:</strong> Tacana.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Pasaron de la reducción misional franciscana a la esclavitud cauchera. En el siglo XX, su sedentarización fue moldeada por misiones lingüísticas.</p><h3>Organización Social y Economía</h3><p>Su ingreso monetario fuerte es la zafra de la castaña en época de lluvias, complementado con roza y quema, caza y pesca ribereña.</p><h3>Situación Actual</h3><p>Sufren directamente el impacto de la minería aurífera y el vertido de mercurio en las cuencas que contaminan su sustento principal.</p>"
        color_mapa = "#16A085"
        coords = "[[-13.0, -67.0], [-12.5, -67.0], [-12.5, -66.2], [-13.0, -66.2]]"
    },
    @{
        id = "cayubaba"
        prefijo_foto = "cayubaba"
        menu_nombre = "8. Cayubaba"
        titulo = "Cayubaba"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (Exaltación).</li><li><strong>Ecosistema:</strong> Sabanas, lagunas y selvas.</li><li><strong>Familia Lingüística:</strong> Aislada.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Antiguo cacicazgo asimilado pacíficamente por los jesuitas (1704). Sufrieron fuerte desestructuración durante el auge gomero.</p><h3>Organización Social y Economía</h3><p>Navegantes tradicionales, sostienen su economía en la pesca, la siembra de arroz y maíz, y el tejido de artesanías en hoja de palmera.</p><h3>Situación Actual</h3><p>Su idioma ha desaparecido casi por completo, pero mantienen una férrea identidad política defendiendo su espacio ante concesiones forestales.</p>"
        color_mapa = "#27AE60"
        coords = "[[-13.3, -65.5], [-12.8, -65.5], [-12.8, -65.0], [-13.3, -65.0]]"
    },
    @{
        id = "chacobo"
        prefijo_foto = "chacobo"
        menu_nombre = "9. Chácobo"
        titulo = "Chácobo"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni.</li><li><strong>Ecosistema:</strong> Bosque alto amazónico.</li><li><strong>Familia Lingüística:</strong> Pano.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Nómadas que escaparon al exterminio cauchero internándose en zonas impenetrables. Contactados formalmente recién a partir de 1955.</p><h3>Organización Social y Economía</h3><p>Pilar de recolección comercial de castaña y palmito. Son uno de los pocos grupos que conservan sus atuendos de corteza y tradiciones ancestrales vigorosas.</p><h3>Situación Actual</h3><p>Vitalidad lingüística excelente. Han consolidado una TCO extensa que administran con proyectos forestales propios, pese a la presión furtiva.</p>"
        color_mapa = "#F39C12"
        coords = "[[-12.2, -66.5], [-11.7, -66.5], [-11.7, -65.8], [-12.2, -65.8]]"
    },
    @{
        id = "chiman"
        prefijo_foto = "chiman"
        menu_nombre = "10. Chimán"
        titulo = "Chimán"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Beni (Ballivián y Moxos).</li><li><strong>Ecosistema:</strong> Pie de monte andino.</li><li><strong>Familia Lingüística:</strong> Mosetén.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Mantuvo una feroz autonomía frente al contacto misional y estatal hasta mediados del siglo XX, refugiándose en el río Maniqui.</p><h3>Organización Social y Economía</h3><p>Excelentes pescadores con arco y barbasco. La comunidad se organiza laxamente en familias dispersas a lo largo de las orillas.</p><h3>Situación Actual</h3><p>Poseen renombre internacional debido a su excelente salud cardiovascular. Su idioma está completamente preservado, pero sus bosques enfrentan masiva invasión maderera.</p>"
        color_mapa = "#8E44AD"
        coords = "[[-15.0, -66.8], [-14.2, -66.8], [-14.2, -66.0], [-15.0, -66.0]]"
    },
    @{
        id = "chiquitano"
        prefijo_foto = "chiquitano"
        menu_nombre = "11. Chiqui"
        titulo = "Chiquitano"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Santa Cruz (Chiquitania).</li><li><strong>Ecosistema:</strong> Bosque seco tropical.</li><li><strong>Familia Lingüística:</strong> Macro-Jê.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Nacidos de un proceso de etnogénesis en las misiones jesuíticas. Soportaron la esclavitud hacendaria tras la expulsión religiosa del siglo XVIII.</p><h3>Organización Social y Economía</h3><p>Grandes agricultores, constructores y músicos barrocos. Se organizan en una poderosa red de cacicazgos comunitarios.</p><h3>Situación Actual</h3><p>Son el grupo mayoritario en tierras bajas. Están en primera línea de combate contra avasallamientos, incendios forestales y avance del agronegocio.</p>"
        color_mapa = "#D35400"
        coords = "[[-17.8, -62.5], [-15.5, -62.5], [-15.5, -59.5], [-17.8, -59.5]]"
    },
    @{
        id = "eseejja"
        prefijo_foto = "eseejja"
        menu_nombre = "12. Ese Ejja"
        titulo = "Ese Ejja"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Pando, Beni y La Paz.</li><li><strong>Ecosistema:</strong> Riberas amazónicas.</li><li><strong>Familia Lingüística:</strong> Tacana.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Grupos nómadas acuáticos. Su contacto estatal se intensificó con los frentes extractivos gomeros y castañeros del siglo XX.</p><h3>Organización Social y Economía</h3><p>Toda su vida se articula en torno a los grandes ríos. La pesca es su actividad comercial y de subsistencia primaria.</p><h3>Situación Actual</h3><p>Vulnerabilidad extrema. Muchas comunidades periurbanas (como en Riberalta) enfrentan graves problemas de desnutrición y contaminación por mercurio minero.</p>"
        color_mapa = "#2980B9"
        coords = "[[-11.5, -67.5], [-10.8, -67.5], [-10.8, -66.5], [-11.5, -66.5]]"
    },
    @{
        id = "guarani"
        prefijo_foto = "guarani"
        menu_nombre = "13. Guaraní"
        titulo = "Guaraní"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Santa Cruz, Chuquisaca y Tarija.</li><li><strong>Ecosistema:</strong> Chaco boliviano.</li><li><strong>Familia Lingüística:</strong> Tupí-Guaraní.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Migraron en búsqueda de la 'Tierra sin Mal'. Resistieron el dominio incaico y español hasta su derrota militar en Kuruyuki (1892), cayendo en el sistema de peonaje forzado.</p><h3>Organización Social y Economía</h3><p>Centrados en el cultivo del maíz y estructurados sólidamente a través de la Asamblea del Pueblo Guaraní (APG).</p><h3>Situación Actual</h3><p>Han recuperado tierras y libertades, pero sostienen continuas tensiones con mega-proyectos de extracción de gas y petróleo dentro de sus territorios.</p>"
        color_mapa = "#C0392B"
        coords = "[[-20.5, -64.0], [-18.5, -64.0], [-18.5, -62.5], [-20.5, -62.5]]"
    },
    @{
        id = "guarasugwe"
        prefijo_foto = "guarasugwe"
        menu_nombre = "14. Guarasugwe"
        titulo = "Guarasugwe"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Frontera Santa Cruz/Beni.</li><li><strong>Ecosistema:</strong> Transición amazónica.</li><li><strong>Familia Lingüística:</strong> Tupí-Guaraní.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Nómadas selváticos que evadieron el colonialismo pero sucumbieron frente a la implacable expansión de la extracción cauchera y las enfermedades occidentales.</p><h3>Organización Social y Economía</h3><p>Históricamente, cazadores de grandes dimensiones y recolectores sin asentamientos fijos prolongados.</p><h3>Situación Actual</h3><p>Culturalmente en situación de casi extinción; los pocos sobrevivientes se asimilaron con otros pueblos chiquitanos e itonamas.</p>"
        color_mapa = "#7F8C8D"
        coords = "[[-14.5, -61.5], [-14.0, -61.5], [-14.0, -60.8], [-14.5, -60.8]]"
    },
    @{
        id = "guarayo"
        prefijo_foto = "guarayo"
        menu_nombre = "15. Guarayo"
        titulo = "Guarayo"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Santa Cruz (Provincia Guarayos).</li><li><strong>Ecosistema:</strong> Transición bosque-amazonía.</li><li><strong>Familia Lingüística:</strong> Tupí-Guaraní.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Fueron evangelizados por misiones franciscanas, las cuales impulsaron una profunda tradición musical que hoy es patrimonio de la etnia.</p><h3>Organización Social y Economía</h3><p>Su economía pivota sobre la agricultura y, esencialmente, la extracción de madera. Son luthiers reconocidos nacionalmente.</p><h3>Situación Actual</h3><p>El territorio Guarayo es escenario crítico de conflicto por avasallamientos ilegales y tráfico de tierras forestales, lo que amenaza su paz comunal.</p>"
        color_mapa = "#16A085"
        coords = "[[-16.5, -63.8], [-15.5, -63.8], [-15.5, -62.8], [-16.5, -62.8]]"
    },
    @{
        id = "itonama"
        prefijo_foto = "itonama"
        menu_nombre = "16. Itonama"
        titulo = "Itonama"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Beni (Provincia Iténez).</li><li><strong>Ecosistema:</strong> Sabanas inundables y bosque ribereño.</li><li><strong>Familia Lingüística:</strong> Aislada.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Reducidos en misiones jesuíticas y posteriormente despojados de sus grandes territorios comunales durante el inicio del modelo ganadero hacendatario republicano.</p><h3>Organización Social y Economía</h3><p>Integrados como fuerza laboral de las grandes estancias. Las mujeres son afamadas por el fino tejido de hamacas de algodón crudo.</p><h3>Situación Actual</h3><p>Lengua en inminente extinción. Exigen al Estado la recuperación de tierras agrícolas que quedaron atrapadas dentro de concesiones privadas.</p>"
        color_mapa = "#F1C40F"
        coords = "[[-13.8, -64.2], [-13.4, -64.2], [-13.4, -63.5], [-13.8, -63.5]]"
    },
    @{
        id = "joaquiniano"
        prefijo_foto = "joaquiniano"
        menu_nombre = "17. Joaquiniano"
        titulo = "Joaquiniano"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Beni (Provincia Mamoré).</li><li><strong>Ecosistema:</strong> Sabanas inundables amazónicas.</li><li><strong>Familia Lingüística:</strong> Arawak (dialecto Baure).</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Se desprendieron del pueblo Baure tras migraciones forzadas para evitar epidemias durante el régimen jesuítico, forjando su identidad propia en San Joaquín.</p><h3>Organización Social y Economía</h3><p>Dependientes del sistema ganadero departamental, complementado con el cultivo de yuca, caza y abundante pesca estacional.</p><h3>Situación Actual</h3><p>En fuerte lucha contra la asimilación total, buscando revitalizar su idioma originario y el reconocimiento oficial de territorios ancestrales que eviten la migración joven.</p>"
        color_mapa = "#3498DB"
        coords = "[[-13.3, -64.8], [-12.9, -64.8], [-12.9, -64.2], [-13.3, -64.2]]"
    },
    @{
        id = "lecos"
        prefijo_foto = "lecos"
        menu_nombre = "18. Lecos"
        titulo = "Lecos"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> La Paz (Larecaja, Franz Tamayo, Guanay).</li><li><strong>Ecosistema:</strong> Subtrópico y pie de monte andino.</li><li><strong>Familia Lingüística:</strong> Leco (Aislada).</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Jugaron un papel crucial en la fundación de misiones franciscanas y posteriormente como milicianos aguerridos durante la Guerra de Independencia boliviana.</p><h3>Organización Social y Economía</h3><p>Fueron excelentes navegantes del río Mapiri y Tipuani. Hoy en día su economía está fuertemente ligada a la agricultura, el cultivo de café y la minería aurífera cooperativizada.</p><h3>Situación Actual</h3><p>Experimentan una revitalización cultural impulsada por organizaciones matrices, a pesar de que la minería plantea serios retos ambientales y divisiones internas.</p>"
        color_mapa = "#9B59B6"
        coords = "[[-15.5, -68.2], [-14.8, -68.2], [-14.8, -67.5], [-15.5, -67.5]]"
    },
    @{
        id = "machineri"
        prefijo_foto = "machineri"
        menu_nombre = "19. Machineri"
        titulo = "Machineri"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento de Pando (Municipio Bolpebra).</li><li><strong>Ecosistema:</strong> Selva amazónica pura (frontera trinacional).</li><li><strong>Familia Lingüística:</strong> Arawak.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Sobrevivieron a la fiebre del caucho manteniéndose en constante movilidad a través de las fronteras de Bolivia, Brasil y Perú, evadiendo el sometimiento total de los patrones gomeros.</p><h3>Organización Social y Economía</h3><p>Son cazadores y recolectores expertos, combinando la agricultura en pequeños chacos familiares con un alto grado de conocimiento forestal tradicional.</p><h3>Situación Actual</h3><p>Enfrentan alta presión por empresas forestales y la cacería furtiva. Su ubicación limítrofe genera complejidades jurisdiccionales para la defensa de sus derechos constitucionales.</p>"
        color_mapa = "#34495E"
        coords = "[[-11.2, -69.5], [-10.8, -69.5], [-10.8, -69.1], [-11.2, -69.1]]"
    },
    @{
        id = "maropa"
        prefijo_foto = "maropa"
        menu_nombre = "20. Maropa"
        titulo = "Maropa"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (Provincia Ballivián, Reyes).</li><li><strong>Ecosistema:</strong> Transición de pampas a selva.</li><li><strong>Familia Lingüística:</strong> Tacana.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Históricamente agrupados en la misión jesuítica de Los Reyes. Su organización tradicional fue desmantelada cuando fueron convertidos en fuerza laboral esencial para la ganadería y extracción de madera republicana.</p><h3>Organización Social y Economía</h3><p>El trabajo asalariado en estancias ganaderas, la carpintería y la pequeña agricultura en áreas periurbanas definen su economía contemporánea.</p><h3>Situación Actual</h3><p>Su idioma, el reyesano, se halla en estado crítico. La lucha política actual se orienta a frenar la asimilación urbana y asegurar parcelas de subsistencia comunitaria.</p>"
        color_mapa = "#E67E22"
        coords = "[[-14.5, -67.4], [-14.0, -67.4], [-14.0, -66.8], [-14.5, -66.8]]"
    },
    @{
        id = "more"
        prefijo_foto = "more"
        menu_nombre = "21. Moré"
        titulo = "Moré"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (frontera con Brasil).</li><li><strong>Ecosistema:</strong> Selva de llanura y riberas del río Guaporé.</li><li><strong>Familia Lingüística:</strong> Chapacura.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Mantuvo una fuerte hostilidad contra las invasiones coloniales. Fueron reducidos temporalmente pero recobraron autonomía hasta que la explotación de goma los fragmentó casi por completo en el siglo XX.</p><h3>Organización Social y Economía</h3><p>La agricultura de roza y quema, la recolección de goma estacional y la pesca en el río Iténez componen su estructura económica base.</p><h3>Situación Actual</h3><p>Tienen un demográfico sumamente reducido. Buscan consolidar áreas de manejo protegido frente al contrabando de madera en la frontera binacional.</p>"
        color_mapa = "#2ECC71"
        coords = "[[-13.0, -64.5], [-12.5, -64.5], [-12.5, -63.8], [-13.0, -63.8]]"
    },
    @{
        id = "moseten"
        prefijo_foto = "moseten"
        menu_nombre = "22. Mosetén"
        titulo = "Mosetén"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> La Paz y Beni.</li><li><strong>Ecosistema:</strong> Subtrópico de los Yungas y pie de monte.</li><li><strong>Familia Lingüística:</strong> Mosetén (Aislada).</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Contactados inicialmente por misiones franciscanas, desarrollaron una economía de intercambio fluido entre la zona andina y las tierras bajas amazónicas desde tiempos coloniales.</p><h3>Organización Social y Economía</h3><p>Grandes productores de frutas, madera y cacao, orientados fuertemente a los mercados locales a través de la OPIM.</p><h3>Situación Actual</h3><p>Poseen una organización estable, sin embargo, el avance agresivo de colonizadores andinos hacia sus territorios genera permanentes conflictos por la tierra.</p>"
        color_mapa = "#8E44AD"
        coords = "[[-15.8, -67.5], [-15.2, -67.5], [-15.2, -66.8], [-15.8, -66.8]]"
    },
    @{
        id = "movima"
        prefijo_foto = "movima"
        menu_nombre = "23. Movima"
        titulo = "Movima"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (Santa Ana del Yacuma).</li><li><strong>Ecosistema:</strong> Llanos, sabanas y humedales de Moxos.</li><li><strong>Familia Lingüística:</strong> Aislada.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Agrupados en misiones jesuíticas. En la época republicana, sufrieron la transformación de su territorio en grandes estancias donde fueron integrados bajo regímenes patronales duros.</p><h3>Organización Social y Economía</h3><p>La cacería y agricultura tradicional convive con la fuerte dependencia del trabajo asalariado en estancias ganaderas. Mantienen viva la autoridad histórica del Gran Cabildo Indigenal.</p><h3>Situación Actual</h3><p>Es uno de los pueblos originarios del Beni con mayor presencia demográfica, trabajando activamente en documentar y revitalizar su excepcional y única lengua aislada.</p>"
        color_mapa = "#F39C12"
        coords = "[[-14.2, -65.8], [-13.5, -65.8], [-13.5, -65.2], [-14.2, -65.2]]"
    },
    @{
        id = "moxeno"
        prefijo_foto = "moxeno"
        menu_nombre = "24. Moxeño"
        titulo = "Moxeño"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (Cercado, Moxos, Marbán).</li><li><strong>Ecosistema:</strong> Sabanas inundables y selvas.</li><li><strong>Familia Lingüística:</strong> Arawak.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Herederos directos de la portentosa cultura constructora de lomas y canales precolombinos. Constituyeron el epicentro del estado misional jesuita y fueron la cuna de masivas rebeliones indígenas republicanas lideradas por la 'Loma Santa'.</p><h3>Organización Social y Economía</h3><p>Tradición agrícola, complementada con ganadería menor y producción excepcional de artesanías. Sus Cabildos son instituciones de enorme peso político.</p><h3>Situación Actual</h3><p>Poseen gran influencia política departamental y nacional. Enfrentan problemas por la construcción de carreteras que fracturan su territorio tradicional.</p>"
        color_mapa = "#27AE60"
        coords = "[[-15.5, -65.5], [-14.5, -65.5], [-14.5, -64.2], [-15.5, -64.2]]"
    },
    @{
        id = "nahua"
        prefijo_foto = "nahua"
        menu_nombre = "25. Nahua"
        titulo = "Nahua"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Pando (Reserva Nacional Manuripi).</li><li><strong>Ecosistema:</strong> Bosque amazónico primario.</li><li><strong>Familia Lingüística:</strong> Pano.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Son uno de los pocos pueblos documentados en Bolivia en estado de Aislamiento Voluntario. Rechazaron todo contacto estatal huyendo a las profundidades de la selva para escapar del sistema cauchero.</p><h3>Organización Social y Economía</h3><p>Basada en el nomadismo absoluto y la invisibilidad. Son cazadores y recolectores itinerantes que evitan el asentamiento prolongado y las infraestructuras modernas.</p><h3>Situación Actual</h3><p>La Constitución protege su derecho al aislamiento. Sus vidas corren un riesgo crítico por choques biológicos si entran en contacto con taladores ilegales o patrullas militares fronterizas.</p>"
        color_mapa = "#34495E"
        coords = "[[-11.8, -69.0], [-11.3, -69.0], [-11.3, -68.4], [-11.8, -68.4]]"
    },
    @{
        id = "pacahuara"
        prefijo_foto = "pacahuara"
        menu_nombre = "26. Pacahuara"
        titulo = "Pacahuara"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Beni y Pando.</li><li><strong>Ecosistema:</strong> Selva amazónica.</li><li><strong>Familia Lingüística:</strong> Pano.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Históricamente nómadas. Fueron cazados y forzados al trabajo durante el auge gomero. Los sobrevivientes se aislaron hasta que fueron contactados y trasladados forzosamente junto al pueblo Chácobo en la década de 1960.</p><h3>Organización Social y Economía</h3><p>Dependen de los recursos que ofrece el bosque, dominando recolección, caza y agricultura incipiente.</p><h3>Situación Actual</h3><p>Representa uno de los casos de vulnerabilidad cultural más urgentes y dramáticos, considerados demográficamente extintos en estado de pureza, asimilados profundamente por la cultura Chácoba.</p>"
        color_mapa = "#16A085"
        coords = "[[-11.5, -67.2], [-11.0, -67.2], [-11.0, -66.7], [-11.5, -66.7]]"
    },
    @{
        id = "quechua"
        prefijo_foto = "quechua"
        menu_nombre = "27. Quechua"
        titulo = "Quechua"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Chuquisaca, Cochabamba, Potosí, Oruro.</li><li><strong>Ecosistema:</strong> Valles andinos, altiplano y subtrópico.</li><li><strong>Familia Lingüística:</strong> Quechua.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Su idioma se expandió durante el Imperio Inca (Tawantinsuyu) y luego fue utilizado y diseminado masivamente por los misioneros españoles como lengua franca colonial. Han sido la columna vertebral del trabajo minero histórico del país.</p><h3>Organización Social y Economía</h3><p>Originalmente ligados al sistema de Ayllus, hoy son la fuerza económica más diversificada del país: abarcan la agricultura comercial intensiva, la minería, el comercio exterior, y el transporte.</p><h3>Situación Actual</h3><p>Son la población indígena más grande de Bolivia. El idioma quechua goza de vitalidad extrema. Sin embargo, su expansión por migración hacia las tierras bajas genera tensiones geopolíticas y agrarias con los pueblos orientales.</p>"
        color_mapa = "#C0392B"
        coords = "[[-20.0, -66.5], [-17.5, -66.5], [-17.5, -64.5], [-20.0, -64.5]]"
    },
    @{
        id = "siriono"
        prefijo_foto = "siriono"
        menu_nombre = "28. Sirionó"
        titulo = "Sirionó"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento del Beni (Casarabe).</li><li><strong>Ecosistema:</strong> Selva amazónica tupida.</li><li><strong>Familia Lingüística:</strong> Tupí-Guaraní.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Famosos cazadores nómadas del bosque oscuro. Su sedentarización forzada por grupos evangélicos provocó la pérdida casi total del conocimiento de cacería tradicional y dependencia a los bienes externos a mediados del siglo XX.</p><h3>Organización Social y Economía</h3><p>Hoy se dedican a la extracción forestal de pequeña escala, venta de miel silvestre y recolección. El tejido en fibras de palma es de altísima calidad cultural.</p><h3>Situación Actual</h3><p>Una población muy pequeña y asimilada en Casarabe. Han sufrido la deforestación brutal de sus territorios tradicionales, lo cual hizo insostenible su estilo de vida histórico de cazadores.</p>"
        color_mapa = "#2980B9"
        coords = "[[-14.9, -64.5], [-14.5, -64.5], [-14.5, -64.0], [-14.9, -64.0]]"
    },
    @{
        id = "tacana"
        prefijo_foto = "tacana"
        menu_nombre = "29. Tacana"
        titulo = "Tacana"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Norte de La Paz.</li><li><strong>Ecosistema:</strong> Amazonía andina (Madidi).</li><li><strong>Familia Lingüística:</strong> Tacana.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Reducidos en misiones franciscanas. Su historia está marcada por ser la puerta de entrada a la Amazonía desde los Andes, sufriendo la explotación forestal e imponiendo barracas caucheras sobre sus poblados históricos.</p><h3>Organización Social y Economía</h3><p>Destacan como vanguardia en el ecoturismo sostenible y manejo de la biodiversidad en el Parque Nacional Madidi. Además practican la agricultura y el tejido tradicional de corteza.</p><h3>Situación Actual</h3><p>Políticamente sólidos, han titularizado una TCO ejemplar. Sin embargo, se ven amenazados por megaproyectos hidroeléctricos gubernamentales que inundarían vastas zonas de su selva.</p>"
        color_mapa = "#27AE60"
        coords = "[[-14.5, -68.5], [-13.5, -68.5], [-13.5, -67.5], [-14.5, -67.5]]"
    },
    @{
        id = "tapiete"
        prefijo_foto = "tapiete"
        menu_nombre = "30. Tapiete"
        titulo = "Tapiete"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento de Tarija.</li><li><strong>Ecosistema:</strong> Chaco seco (río Pilcomayo).</li><li><strong>Familia Lingüística:</strong> Tupí-Guaraní.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Su historia está marcada por la Guerra del Chaco, donde su territorio ancestral fue escenario militar. Muchos fueron tomados prisioneros, desplazados o utilizados como guías forzosos para el ejército boliviano.</p><h3>Organización Social y Economía</h3><p>Su economy orbita estrictamente en torno a la pesca (el sábalo) en el río Pilcomayo y la recolección de frutos chaqueños. Poseen clanes matriarcales remanentes.</p><h3>Situación Actual</h3><p>Las severas sequías, agravadas por el desvío y desecación del río Pilcomayo debido a megaproyectos en países vecinos, han colapsado su base económica principal: la pesca estacional.</p>"
        color_mapa = "#E67E22"
        coords = "[[-22.0, -62.8], [-21.5, -62.8], [-21.5, -62.3], [-22.0, -62.3]]"
    },
    @{
        id = "toromona"
        prefijo_foto = "toromona"
        menu_nombre = "31. Toromona"
        titulo = "Toromona"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> La Paz (Parque Nacional Madidi, zona intangible).</li><li><strong>Ecosistema:</strong> Bosque amazónico primario virgen.</li><li><strong>Familia Lingüística:</strong> Tacana (presumible).</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Nunca fueron sometidos, ni por los incas, ni por españoles, ni por el Estado. Representan la última resistencia de autonomía indígena radical del norte boliviano, internándose deliberadamente en la selva en el siglo XIX.</p><h3>Organización Social y Economía</h3><p>Se asume que son cazadores-recolectores puros en situación de aislamiento voluntario extremo, desconociéndose datos demográficos precisos o su organización interna actual.</p><h3>Situación Actual</h3><p>Bolivia ha declarado reservas intangibles exclusivas para su protección. El contacto con madereros ilegales o exploradores biológicos significa el riesgo de aniquilación total por falta de anticuerpos.</p>"
        color_mapa = "#34495E"
        coords = "[[-13.5, -68.8], [-13.0, -68.8], [-13.0, -68.2], [-13.5, -68.2]]"
    },
    @{
        id = "uru"
        prefijo_foto = "uru"
        menu_nombre = "32. Uru"
        titulo = "Uru"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamentos de Oruro y La Paz.</li><li><strong>Ecosistema:</strong> Eje acuático andino (Lagos Poopó y Titicaca).</li><li><strong>Familia Lingüística:</strong> Uru-Chipaya.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Se autodenominan los 'Hombres del Agua', siendo anteriores a los señoríos aymaras y los incas. Su vida flotaba literalmente sobre islas artificiales de totora en el sistema lacustre andino milenario.</p><h3>Organización Social y Economía</h3><p>Económicamente dependientes al 100% de la caza de aves acuáticas, la pesca y las complejas artesanías textiles fabricadas con fibra vegetal de totora.</p><h3>Situación Actual</h3><p>Afrontan una tragedia ecológica monumental. La reciente y repetida sequía extrema del lago Poopó (junto a la contaminación minera) ha destruido completamente su hábitat y economía, forzándolos a la marginación y al trabajo rural atípico.</p>"
        color_mapa = "#3498DB"
        coords = "[[-19.0, -68.0], [-18.5, -68.0], [-18.5, -67.5], [-19.0, -67.5]]"
    },
    @{
        id = "weenhayek"
        prefijo_foto = "weenhayek"
        menu_nombre = "33. Weenhayek"
        titulo = "Weenhayek"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento de Tarija (Yacuiba, Villa Montes).</li><li><strong>Ecosistema:</strong> Chaco boliviano (cuenca del Pilcomayo).</li><li><strong>Familia Lingüística:</strong> Mataco-Maca.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Fueron cazadores nómadas pacificados progresivamente por misiones suecas en el siglo XX. Sufrieron el fuerte impacto destructivo en sus áreas de caza debido al desarrollo de la industria petrolera nacional.</p><h3>Organización Social y Economía</h3><p>Maestros de la artesanía con hilo vegetal de 'caraguatá'. Su base alimentaria y económica es el comercio de pesca (sábalo y surubí) cuando el río Pilcomayo se encuentra estable.</p><h3>Situación Actual</h3><p>Comparten la misma tragedia que los Tapietes por el colapso del caudal y contaminación minera de los grandes ríos chaqueños, enfrentando elevados picos de pobreza urbana departamental.</p>"
        color_mapa = "#9B59B6"
        coords = "[[-21.8, -63.5], [-21.2, -63.5], [-21.2, -62.8], [-21.8, -62.8]]"
    },
    @{
        id = "yaminahua"
        prefijo_foto = "yaminahua"
        menu_nombre = "34. Yaminahua"
        titulo = "Yaminahua"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento de Pando (Provincia Nicolás Suárez).</li><li><strong>Ecosistema:</strong> Selva amazónica pura.</li><li><strong>Familia Lingüística:</strong> Pano.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Fueron víctimas absolutas del régimen de esclavitud extractivista durante el apogeo de la goma, fraccionándose en grupos familiares que se movilizan constantemente por las selvas de Perú y Bolivia buscando evadir abusos.</p><h3>Organización Social y Economía</h3><p>Comunidades de pequeña escala y estacionalmente itinerantes. Priorizan el conocimiento de caza, pesca y recolección silvestre, complementado escasamente por agricultura.</p><h3>Situación Actual</h3><p>Población mínima. Al habitar zonas limítrofes porosas, sus derechos son constantemente vulnerados por traficantes de madera y fauna silvestre brasileños y peruanos.</p>"
        color_mapa = "#16A085"
        coords = "[[-11.2, -69.2], [-10.8, -69.2], [-10.8, -68.8], [-11.2, -68.8]]"
    },
    @{
        id = "yuqui"
        prefijo_foto = "yuqui"
        menu_nombre = "35. Yuqui"
        titulo = "Yuqui"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Departamento de Cochabamba (Provincia Carrasco).</li><li><strong>Ecosistema:</strong> Subtrópico amazónico.</li><li><strong>Familia Lingüística:</strong> Tupí-Guaraní.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Cazadores-recolectores nómadas obligados al sedentarismo por misiones de la 'Nueva Tribu' en la década de 1970. El choque fue traumático, causando altos índices de mortalidad por tuberculosis.</p><h3>Organización Social y Economía</h3><p>La agricultura a gran escala es ajena a su cultura. Se dedican a la artesanía de arcos, cestería, pesca y trabajo jornalero menor. Carecen de estructuras de liderazgo vertical históricas.</p><h3>Situación Actual</h3><p>Alta vulnerabilidad médica y exclusión social severa. Sus territorios han sido sistemáticamente ocupados (avasallados) por el avance de las plantaciones de coca dirigidas por sectores migrantes andinos.</p>"
        color_mapa = "#C0392B"
        coords = "[[-16.8, -64.8], [-16.4, -64.8], [-16.4, -64.3], [-16.8, -64.3]]"
    },
    @{
        id = "yuracare"
        prefijo_foto = "yuracare"
        menu_nombre = "36. Yuracaré"
        titulo = "Yuracaré"
        fotos = 3
        ficha = "<ul><li><strong>Ubicación Geográfica:</strong> Cochabamba y Beni (TIPNIS).</li><li><strong>Ecosistema:</strong> Pie de monte y Amazonía tropical.</li><li><strong>Familia Lingüística:</strong> Aislada.</li></ul>"
        texto = "<h3>Contexto Histórico</h3><p>Mantuvieron sus redes comerciales fluviales de manera eficiente por siglos, evadiendo pacíficamente los rígidos intentos de agrupamiento misional por parte del clero colonial a través del movimiento libre por los ríos.</p><h3>Organización Social y Economía</h3><p>Cazadores muy habilidosos (flecheros), desarrollan la agricultura de plátano, yuca y arroz. Su maestría en la navegación de ríos tributarios al Chapare sigue siendo vital.</p><h3>Situación Actual</h3><p>Junto a los Moxeños, lideran la defensa legal, política y ecológica del Territorio Indígena y Parque Nacional Isiboro-Sécure (TIPNIS), un enclave esencial para la biodiversidad frente al desarrollo carretero y la expansión cocalera.</p>"
        color_mapa = "#2ECC71"
        coords = "[[-16.5, -66.0], [-15.5, -66.0], [-15.5, -65.2], [-16.5, -65.2]]"
    }
)

# Construcción unificada de componentes navegacionales
$menuNavegacion = ""
$mosaicoMovil = ""

foreach ($etnia in $etnias) {
    $menuNavegacion += "<a href='$($etnia.id).html' id='nav-$($etnia.id)'>$($etnia.menu_nombre)</a>`n        "
    $mosaicoMovil += "<a href='$($etnia.id).html' class='mosaico-item' id='mos-$($etnia.id)'>$($etnia.titulo)</a>`n            "
}

Write-Host "Iniciando compilación Definitiva y sin truncados..." -ForegroundColor Cyan

# --- CONSTRUCCIÓN INDEPENDIENTE DE INDEX.HTML ---
$indexTemplate = @"
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Amazonía - Inicio</title>
    <style>
        :root { --accent-gold: #FFB81C; --dark-bg: #121212; }
        body { font-family: 'Segoe UI', sans-serif; background-color: var(--dark-bg); color: #fff; margin: 0; padding: 20px; text-align: center; }
        header { padding: 40px 0; border-bottom: 2px solid var(--accent-gold); margin-bottom: 40px; }
        h1 { text-transform: uppercase; letter-spacing: 2px; }
        .grid-portal { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; max-width: 1000px; margin: 0 auto; padding-bottom: 50px; }
        .etnia-link { background: #1a1a1a; padding: 20px; border-radius: 8px; text-decoration: none; color: #ddd; border: 1px solid #333; font-weight: bold; transition: 0.3s; display: block; }
        .etnia-link:hover { background: var(--accent-gold); color: #000; border-color: var(--accent-gold); }
    </style>
</head>
<body>
    <header><h1>Portal Amazonía</h1><p>Seleccione una nación originaria para continuar</p></header>
    <div class="grid-portal">
        {{MOSAICO_COMPLETO}}
    </div>
</body>
</html>
"@

$mosaicoCompleto = ""
foreach ($etnia in $etnias) {
    $mosaicoCompleto += "<a href='$($etnia.id).html' class='etnia-link'>$($etnia.titulo)</a>`n        "
}
$indexFinal = $indexTemplate -replace '\{\'\{\{MOSAICO_COMPLETO\}\}\'\}', $mosaicoCompleto
$indexFinal = $indexTemplate.Replace("{{MOSAICO_COMPLETO}}", $mosaicoCompleto)
[System.IO.File]::WriteAllText("$PWD\indigenas.html", $indexFinal, $utf8NoBom)
Write-Host " [+] Portal de indígenas (indigenas.html) creado exitosamente." -ForegroundColor Green

# --- INYECCIÓN EN MÓDULOS DE PÁGINAS INDIVIDUALES ---
foreach ($etnia in $etnias) {
    Write-Host "Procesando matriz para: $($etnia.titulo)" -ForegroundColor Yellow
    
    $htmlFinal = $plantillaHTML

    # Reemplazos estructurales
    $htmlFinal = $htmlFinal.Replace("{{ID_ETNIA}}", $etnia.id)
    $htmlFinal = $htmlFinal.Replace("{{TITULO_ETNIA}}", $etnia.titulo)
    $htmlFinal = $htmlFinal.Replace("{{FICHA_TECNICA}}", $etnia.ficha)
    $htmlFinal = $htmlFinal.Replace("{{TEXTO_COMPLETO}}", $etnia.texto)
    $htmlFinal = $htmlFinal.Replace("{{COORDENADAS_ETNIA}}", $etnia.coords)
    $htmlFinal = $htmlFinal.Replace("{{COLOR_ETNIA}}", $etnia.color_mapa)
    
    # Menús e Índices Activos por iteración
    $menuActivo = $menuNavegacion -replace "id='nav-$($etnia.id)'", "id='nav-$($etnia.id)' class='activo'"
    $htmlFinal = $htmlFinal.Replace("{{MENU_NAVEGACION}}", $menuActivo)

    $mosaicoActivo = $mosaicoMovil -replace "id='mos-$($etnia.id)'", "id='mos-$($etnia.id)' class='activo'"
    $htmlFinal = $htmlFinal.Replace("{{MOSAICO_MOVIL}}", $mosaicoActivo)

    # Construcción de Álbum con validación explícita de Case-Sensitivity
    $carruselHTML = ""
    for ($i = 1; $i -le $etnia.fotos; $i++) {
        $nombreFoto = $etnia.prefijo_foto
        $carruselHTML += "<div class='slide'><img src='images/$($nombreFoto)$i.jpg' alt='Fotografía $($etnia.titulo) $i' loading='lazy'></div>`n                "
    }
    $htmlFinal = $htmlFinal.Replace("{{IMAGENES_CARRUSEL}}", $carruselHTML)

    # ESCRITURA FORZADA EN ENCODING UTF-8 SIN BOM PARA COMPATIBILIDAD CON HOSTING LINUX
    $nombreArchivo = "$($PWD.Path)\$($etnia.id).html"
    [System.IO.File]::WriteAllText($nombreArchivo, $htmlFinal, $utf8NoBom)
    
    Write-Host "  [✓] Guardado: $($etnia.id).html" -ForegroundColor Green
}

Write-Host "Compilación de Avrora Soft finalizada con éxito absoluto. 36 páginas listas." -ForegroundColor Cyan