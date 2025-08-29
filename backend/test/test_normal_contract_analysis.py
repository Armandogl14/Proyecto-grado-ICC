#!/usr/bin/env python
"""
Test de análisis de contrato NORMAL de alquiler (no problemático)
Comparación con el sistema RAG + ML para validar efectividad
"""

import os
import sys
import django
from typing import List, Dict

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ml_analysis.ml_service import ContractMLService
from legal_knowledge.rag_service import rag_service
from legal_knowledge.models import LegalArticle


def analyze_normal_rental_contract():
    """
    Analiza un contrato NORMAL de alquiler que NO debería tener problemas
    """
    print("🏠 ANÁLISIS DE CONTRATO NORMAL DE ALQUILER (NO PROBLEMÁTICO)")
    print("=" * 70)
    
    # Contrato normal proporcionado por el usuario
    contract_text = """
    CONTRATO DE ARRENDAMIENTO DE VIVIENDA (NORMAL)
    
    PRIMERO: LA PROPIETARIA da en alquiler al EL INQUILINO un Apto. en el segundo nivel, ubicado en la calle Otto Riveras, No. 38-B (altos), Residencial Villa Diana, 7 1/2, Carretera Sánchez, Santo Domingo, Distrito Nacional, 2 habitaciones, un baño, cocina, sala, ante sala, área de lavado, varios balcones y terraza destechada, quien la usara para vivienda, EL INQUILINO, no podrá ceder ni sub-alquilarlo, ni todo ni en parte, sin el consentimiento por escrito de LA PROPIETARIA. Tampoco podrá cederlo gratuitamente, ni por favor o por mera tolerancia admitir que ningún tercero, aun pariente, pueda habitar el Apto. que alquila en calidad de sub-inquilino.

    SEGUNDO: LA PROPIETARIA, garantiza a EL INQUILINO el uso y disfrute pacifico del inmueble arrendado por el tiempo del presente arrendamiento.

    TERCERO: EL INQUILINO queda obligado a mantener El Apto. En perfectas condiciones y a entregarlo al termino del contrato en buen estado Y se constituye en el guardián del citado inmueble, por lo que será responsable ante cualquier catástrofe ocurrida mientras dure este contrato y todos los desperfectos en paredes, pisos, puertas, cristales, pestillos, cerraduras, instalaciones eléctricas, instalaciones sanitarias, (Obstrucción de inodoros, lavamanos, y cualquier otro desagüe, cambio de zapatillas, rotura de llaves, etc.), serán reparados o repuestos por EL INQUILINO a su solo costo, debiendo ser recibido por LA PROPIETARIA a su entera satisfacción. También queda a cargo de EL INQUILINO la pintura interior (Colonial 88 Popular) de la vivienda.

    PÁRRAFO I: EL INQUILINO permitirá el acceso a LA PROPIETARIA al inmueble alquilado, siempre y cuando fuere necesario para realizar cualquier trabajo de mantenimiento que fuere menester y siempre y cuando LA PROPIETARIA notifique a EL INQUILINO por escrito de su visita, por lo menos con tres (3) días de anticipativo.

    CUARTO: EL INQUILINO se compromete a no hacer ningún cambio o distribución nueva en el Apto. sin la previa autorización por escrito de LA PROPIETARIA y, en caso de estas ser autorizadas. Todas las mejoras hechas, incluyendo las instalaciones eléctricas que se hagan con todo su material, quedaran a beneficio de LA PROPIETARIA sin compensación de ninguna especie.

    PÁRRAFO I: Todo daño o perjuicio causado al inmueble por EL INQUILINO que resulten por cualquier causa, de toda índole o naturaleza, consecuencia de descuido, omisión, negligencia, conducta impropia u otras actividades de los empleados, sirvientes, visitantes o relacionados de EL INQUILINO serán reparados a su propio costo y a la entera satisfacción de LA PROPIETARIA.

    QUINTO: EL INQUILINO, queda obligado a pagar la suma de DIESISEIS MIL PESOS DOMINICANOS (RD$16,000.00), suma que pagará los día 21 de cada mes sin retraso algunos, por lo que el INQUILINO acepta pagar una mora de un 5%, al momento del pago una vez vencido un plazo no mayor de cinco días.

    PÁRRAFO I: EL INQUILINO confiere a LA PROPIETARIA la suma en pesos dominicanos, correspondientes a la suma de TREINTA Y DOS MIL PESOS (RD$ 32,000.00), correspondiente por concepto de dos (2) mes de depósitos, suma que LA PROPIETARIA reconoce haber recibido a su entera satisfacción de manos de EL INQUILINO, dándole en consecuencia el correspondiente recibo de descargo total, completo y definitivo por la suma por ella recibida, a que se refiere el presente párrafo. Advirtiéndole a EL INQUILINO que dicha suma no podrá ser aplicada al pago de mensualidades vencidas y de eventuales gastos que ocasione EL INQUILINO, todo conforme al presente contrato.

    SEXTO: El presente contrato tendrá una vigencia de UN (1) año, desde de la firma del mismo y si al término de este periodo, las partes podrán OPTAR por dar termino al presente contrato o renovarlo, por lo que al vencimiento del contrato la parte que opte por el termino deberá dar previo aviso por escrito, con sesenta días (60) antes del término de la vigencia su deseo de rescindirlo.

    SÉPTIMO: Si este contrato se renovase por la tacita reconducción, queda convenido y aceptado por EL INQUILINO un aumento, proporcional a la tasa inflacionaria oficial del banco central de la Republica Dominicana o el equivalente a un 10% seleccionándose para este aumento el mayor de los dos, por cada año de renovación en el precio para el pago del alquiler del citado inmueble, por lo que las oblaciones contraídas por EL INQUILINO Y EL FIADOR se mantendrán hasta que realmente EL INQUILINO entregue el inmueble alquilado y sus llaves a la Propietaria la cual emitirá recibo de descargo por escrito.

    OCTAVO: Queda establecido, que los servicios de agua y recogida de basura serán pagos por la propietaria, y los servicios de luz, contrato 2062649, que ya esta instalado, teléfono, y cualquier otro servicio que entendiere el INQUILINO, necesitare, será por cuenta exclusiva de éste, quien tendrá a su cargo suscribir los contratos con las entidades correspondientes sin injerencia ni responsabilidad alguna para LA PROPIETARIA.

    NOVENO: EL INQUILINO presenta como su FIADOR SOLIDARIO E INDIVISIBLE de todas los compromisos y obligaciones contraídas por EL INQUILINO en el presente Contrato, a la señora LEONILDA BERENICE JIMENEZ, dominicana, soltera, mayor de edad, medico, portador de la cedula de identidad y electoral No. 018-0060178-1, domiciliado y residente en esta ciudad. de Santo Domingo, Distrito Nacional, quien acepta y asume ser codeudor del propietario por todos los pago, en el caso de que EL INQUILINO dejare de hacerlo, tanto de los alquileres dejados de pagar como por los deterioros y danos que le haya ocasionado a el inmueble y sus instalaciones sanitarias y eléctricas, así como de los pagos por servicios además, LA PROPIETARIA tendrá derecho de perseguirlo en cobro del arrendamiento, en caso de no pago de EL INQUILINO, todo al efecto de las obligaciones que por el presente Contrato en su condición de fiador solidario e indivisible, firma al pie de este Contrato.

    DÉCIMO: Sin perjuicio de lo establecido en los artículos precedentes, las obligaciones de EL INQUILINO persistirán hasta el momento en que real y efectivamente entregue a LA PROPIETARIA el inmueble en perfecto estado, las llaves del mismo y los comprobantes de la cancelación del contrato de servicios de Edesur, entrega que se comprobara mediante recibo escrito de LA PROPIETARIA.

    DÉCIMO PRIMERO: RESCISIÓN DEL CONTRATO. En el caso de que EL INQUILINO decida ponerle fin al presente contrato, antes de su vencimiento estará obligado a pagar los alquileres vencidos al momento de la entrega del inmueble, y acepta una penalidad de un mes de renta por el primer año de contrato. Sin perjuicio de lo antes indicado, las obligaciones de EL INQUILINO persistirán hasta el momento en que real y efectivamente entregue de conformidad a LA PROPIETARIA el inmueble alquilado y sus llaves, entrega que se comprobara mediante recibo escrito de LA PROPIETARIA.

    DÉCIMO SEGUNDO: CONDICION INCUMPLIMIENTOS Todas las condiciones del presente contrato de inquilinato son esenciales y rigurosas para las partes. Si EL INQUILINO no cumple una sola de dichas disposiciones, se producirá la resolución del contrato, de pleno derecho. Un (1) mes después de haber sido puesto en mora de pago, y de no acatarse la intimación de que se trate.

    DÉCIMO TERCERO: Las partes de mutuo acuerdo y para lo no pactado, se remiten al derecho común.

    DÉCIMO CUARTO: Para todos los fines del presente Contrato, las partes eligen domicilio en Santo Domingo, Distrito Nacional, con todas sus consecuencias legales.
    """
    
    print("📄 INFORMACIÓN DEL CONTRATO NORMAL:")
    print("  • Tipo: Arrendamiento de vivienda")
    print("  • Ubicación: Residencial Villa Diana, Santo Domingo")
    print("  • Renta: RD$16,000.00 mensuales")
    print("  • Depósito: RD$32,000.00 (2 meses)")
    print("  • Duración: 1 año")
    print("  • Expectativa: CONTRATO NORMAL (no problemático)")
    print()
    
    # 1. Análisis con ML tradicional
    print("🤖 ANÁLISIS ML TRADICIONAL:")
    print("-" * 30)
    
    ml_service = ContractMLService()
    traditional_analysis = ml_service.analyze_contract(contract_text)
    
    print(f"  • Total cláusulas detectadas: {traditional_analysis['total_clauses']}")
    print(f"  • Cláusulas abusivas: {traditional_analysis['abusive_clauses_count']}")
    print(f"  • Risk Score: {traditional_analysis['risk_score']:.3f}")
    print(f"  • Tiempo de procesamiento: {traditional_analysis['processing_time']:.2f}s")
    
    # Interpretación del risk score
    if traditional_analysis['risk_score'] < 0.3:
        risk_level = "🟢 BAJO"
        interpretation = "Contrato con pocas cláusulas problemáticas"
    elif traditional_analysis['risk_score'] < 0.7:
        risk_level = "🟡 MEDIO"
        interpretation = "Contrato con algunas cláusulas que requieren atención"
    else:
        risk_level = "🔴 ALTO"
        interpretation = "Contrato con varias cláusulas problemáticas"
    
    print(f"  • Nivel de riesgo: {risk_level}")
    print(f"  • Interpretación: {interpretation}")
    
    # 2. Análisis de cláusulas específicas que suelen ser problemáticas
    print("\n🔍 ANÁLISIS DE CLÁUSULAS ESPECÍFICAS:")
    print("-" * 40)
    
    potentially_problematic_clauses = [
        {
            "name": "Responsabilidad por catástrofes",
            "text": "será responsable ante cualquier catástrofe ocurrida mientras dure este contrato",
            "expected": "Podría ser problemática - responsabilidad muy amplia"
        },
        {
            "name": "Aumento del 10%",
            "text": "un aumento, proporcional a la tasa inflacionaria oficial del banco central de la Republica Dominicana o el equivalente a un 10% seleccionándose para este aumento el mayor de los dos",
            "expected": "Similar al contrato anterior - podría ser problemática"
        },
        {
            "name": "Penalidad por rescisión",
            "text": "acepta una penalidad de un mes de renta por el primer año de contrato",
            "expected": "Similar al anterior - pero normal en RD"
        }
    ]
    
    for clause in potentially_problematic_clauses:
        print(f"\n🔎 {clause['name']}:")
        print(f"Fragmento: {clause['text'][:80]}...")
        print(f"Expectativa: {clause['expected']}")
        
        # Análisis ML individual
        ml_prediction = ml_service.classifier_pipeline.predict([clause['text']])[0]
        ml_probability = ml_service.classifier_pipeline.predict_proba([clause['text']])[0]
        
        prediction_text = "🔴 Abusiva" if ml_prediction == 1 else "🟢 Válida"
        print(f"Predicción ML: {prediction_text} (prob: {ml_probability[1]:.3f})")
        
        # Búsqueda RAG
        rag_results = rag_service.search_articles(clause['text'], tema_filter="alquileres", max_results=1)
        if rag_results:
            article = rag_results[0]
            print(f"Artículo relevante: {article['ley_asociada']} Art. {article['articulo']} (sim: {article['similarity_score']:.3f})")
    
    # 3. Comparación con el contrato anterior
    print("\n📊 COMPARACIÓN CON CONTRATO ANTERIOR:")
    print("-" * 40)
    
    # Datos del contrato anterior (problemático)
    previous_contract_stats = {
        'total_clauses': 13,
        'abusive_clauses_count': 9,
        'risk_score': 0.625,
        'processing_time': 22.46
    }
    
    print("CONTRATO ANTERIOR (Problemático):")
    print(f"  • Cláusulas: {previous_contract_stats['total_clauses']}")
    print(f"  • Abusivas: {previous_contract_stats['abusive_clauses_count']}")
    print(f"  • Risk Score: {previous_contract_stats['risk_score']:.3f}")
    
    print("\nCONTRATO ACTUAL (Normal):")
    print(f"  • Cláusulas: {traditional_analysis['total_clauses']}")
    print(f"  • Abusivas: {traditional_analysis['abusive_clauses_count']}")
    print(f"  • Risk Score: {traditional_analysis['risk_score']:.3f}")
    
    # Cálculo de diferencias
    clause_diff = traditional_analysis['abusive_clauses_count'] - previous_contract_stats['abusive_clauses_count']
    risk_diff = traditional_analysis['risk_score'] - previous_contract_stats['risk_score']
    
    print(f"\nDIFERENCIAS:")
    print(f"  • Cláusulas abusivas: {clause_diff:+d} ({'mejor' if clause_diff < 0 else 'peor'})")
    print(f"  • Risk Score: {risk_diff:+.3f} ({'mejor' if risk_diff < 0 else 'peor'})")
    
    # 4. Búsqueda RAG contextual
    print("\n🔍 BÚSQUEDA RAG CONTEXTUAL:")
    print("-" * 30)
    
    search_terms = ["contrato arrendamiento normal", "obligaciones equilibradas", "fiador solidario"]
    
    for term in search_terms:
        results = rag_service.search_articles(term, tema_filter="alquileres", max_results=2)
        print(f"\n🔎 '{term}': {len(results)} artículos")
        for result in results:
            print(f"  • Art. {result['articulo']} - Score: {result['similarity_score']:.3f}")
    
    # 5. Evaluación final
    print("\n📋 EVALUACIÓN FINAL:")
    print("-" * 25)
    
    print("✅ EXPECTATIVA vs REALIDAD:")
    print(f"  • Expectativa: Contrato NORMAL (no problemático)")
    
    if traditional_analysis['risk_score'] < 0.4:
        reality = "✅ CONFIRMADO - Contrato relativamente normal"
        color = "🟢"
    elif traditional_analysis['risk_score'] < 0.6:
        reality = "⚠️ PARCIAL - Algunas cláusulas problemáticas"
        color = "🟡"
    else:
        reality = "❌ CONTRARIO - Contrato con problemas significativos"
        color = "🔴"
    
    print(f"  • Realidad ML: {reality}")
    print(f"  • Nivel: {color} Risk Score: {traditional_analysis['risk_score']:.3f}")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if traditional_analysis['risk_score'] < 0.4:
        print("  • El contrato parece estar dentro de los parámetros normales")
        print("  • Revisar cláusulas específicas identificadas")
        print("  • Considerar context legal con artículos encontrados")
    else:
        print("  • El contrato requiere revisión detallada")
        print("  • Varias cláusulas podrían ser problemáticas")
        print("  • Comparar con estándares legales dominicanos")
    
    return {
        'analysis': traditional_analysis,
        'comparison': {
            'clause_difference': clause_diff,
            'risk_difference': risk_diff,
            'is_better': risk_diff < 0
        },
        'reality_check': {
            'expected': 'normal',
            'actual_risk': traditional_analysis['risk_score'],
            'matches_expectation': traditional_analysis['risk_score'] < 0.4
        }
    }


def compare_both_contracts():
    """
    Función para comparar ambos contratos analizados
    """
    print("\n🔄 COMPARACIÓN FINAL DE AMBOS CONTRATOS:")
    print("=" * 50)
    
    print("CONTRATO 1 (Problemático según usuario):")
    print("  • Tu evaluación: PROBLEMÁTICO")
    print("  • ML Risk Score: 0.625 🟡")
    print("  • Cláusulas abusivas: 9/13")
    print("  • Resultado: ML detectó problemas parcialmente")
    
    print("\nCONTRATO 2 (Normal según usuario):")
    # Este resultado se obtiene del análisis actual
    print("  • Tu evaluación: NORMAL")
    print("  • ML Risk Score: [A determinar] ")
    print("  • Resultado: [A determinar]")
    
    print("\n🎯 CONCLUSIONES:")
    print("  • El sistema RAG + ML puede distinguir diferentes niveles de riesgo")
    print("  • Las referencias al Código Civil proporcionan contexto legal")
    print("  • El modelo necesita calibración con más datos dominicanos")


def main():
    """Función principal"""
    try:
        # Verificar artículos disponibles
        article_count = LegalArticle.objects.filter(is_active=True).count()
        if article_count == 0:
            print("❌ ERROR: No hay artículos legales cargados.")
            return
        
        print(f"📚 Artículos disponibles: {article_count}")
        
        # Ejecutar análisis del contrato normal
        results = analyze_normal_rental_contract()
        
        # Comparación final
        compare_both_contracts()
        
        print("\n🎉 ANÁLISIS COMPLETO FINALIZADO")
        
        # Estadísticas del sistema
        stats = rag_service.get_statistics()
        print(f"\n📊 ESTADÍSTICAS DEL SISTEMA:")
        print(f"  • Total búsquedas RAG: {stats.get('total_searches', 0)}")
        print(f"  • Artículos alquileres: {stats.get('temas', {}).get('alquileres', 0)}")
        
        # Resumen final
        if results['reality_check']['matches_expectation']:
            print("\n✅ El sistema ML identificó correctamente que es un contrato normal")
        else:
            print("\n⚠️ El sistema ML identificó problemas en un contrato considerado normal")
            print("   Esto sugiere que el modelo necesita ajustes o más datos de entrenamiento")
        
    except Exception as e:
        print(f"❌ ERROR EN ANÁLISIS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()