#!/usr/bin/env python
"""
Resumen comparativo final de ambos contratos analizados
Muestra las diferencias entre las expectativas del usuario y las predicciones del ML
"""

def print_comparative_summary():
    """
    Imprime un resumen comparativo detallado de ambos contratos
    """
    print("🎯 ANÁLISIS COMPARATIVO FINAL - CONTRATOS DE ALQUILER")
    print("=" * 65)
    
    # Datos de ambos contratos
    contract_data = {
        'problematic': {
            'user_label': 'PROBLEMÁTICO',
            'location': 'Ensanche Naco',
            'rent': 'RD$38,000',
            'total_clauses': 13,
            'abusive_clauses': 9,
            'risk_score': 0.625,
            'processing_time': 22.46,
            'risk_level': '🟡 MEDIO',
            'user_expectation': 'Problemático',
            'ml_result': 'Detectó problemas parcialmente'
        },
        'normal': {
            'user_label': 'NORMAL',
            'location': 'Residencial Villa Diana',
            'rent': 'RD$16,000',
            'total_clauses': 14,
            'abusive_clauses': 11,
            'risk_score': 0.638,
            'processing_time': 25.79,
            'risk_level': '🔴 ALTO',
            'user_expectation': 'Normal (no problemático)',
            'ml_result': 'Detectó MÁS problemas de los esperados'
        }
    }
    
    print("📊 DATOS COMPARATIVOS:")
    print("-" * 25)
    
    print(f"{'CRITERIO':<25} {'CONTRATO 1':<20} {'CONTRATO 2':<20}")
    print("-" * 65)
    print(f"{'Evaluación Usuario':<25} {contract_data['problematic']['user_label']:<20} {contract_data['normal']['user_label']:<20}")
    print(f"{'Ubicación':<25} {contract_data['problematic']['location']:<20} {contract_data['normal']['location']:<20}")
    print(f"{'Renta Mensual':<25} {contract_data['problematic']['rent']:<20} {contract_data['normal']['rent']:<20}")
    print(f"{'Total Cláusulas':<25} {contract_data['problematic']['total_clauses']:<20} {contract_data['normal']['total_clauses']:<20}")
    print(f"{'Cláusulas Abusivas':<25} {contract_data['problematic']['abusive_clauses']:<20} {contract_data['normal']['abusive_clauses']:<20}")
    print(f"{'Risk Score ML':<25} {contract_data['problematic']['risk_score']:<20.3f} {contract_data['normal']['risk_score']:<20.3f}")
    print(f"{'Nivel de Riesgo':<25} {contract_data['problematic']['risk_level']:<20} {contract_data['normal']['risk_level']:<20}")
    print(f"{'Tiempo Proceso (s)':<25} {contract_data['problematic']['processing_time']:<20.2f} {contract_data['normal']['processing_time']:<20.2f}")
    
    # Análisis de discrepancias
    print("\n🔍 ANÁLISIS DE DISCREPANCIAS:")
    print("-" * 35)
    
    print("CONTRATO 1 (Etiquetado como 'PROBLEMÁTICO'):")
    print("  ✅ Coincidencia parcial:")
    print("    • El ML detectó nivel medio de problemas (0.625)")
    print("    • 9/13 cláusulas identificadas como abusivas")
    print("    • El análisis coincide con la percepción del usuario")
    
    print("\nCONTRATO 2 (Etiquetado como 'NORMAL'):")
    print("  ❌ Discrepancia significativa:")
    print("    • El ML detectó MAYOR riesgo (0.638 vs 0.625)")
    print("    • 11/14 cláusulas identificadas como abusivas")
    print("    • El ML encontró MÁS problemas de los esperados")
    
    # Cláusulas específicas problemáticas en el contrato "normal"
    print("\n⚠️ CLÁUSULAS PROBLEMÁTICAS EN CONTRATO 'NORMAL':")
    print("-" * 50)
    
    problematic_clauses_normal = [
        "TERCERO: Responsabilidad excesiva por catástrofes y reparaciones",
        "CUARTO: Responsabilidad por daños de visitantes/empleados",
        "NOVENO: Fiador solidario con responsabilidad amplia",
        "DÉCIMO SEGUNDO: Resolución automática por cualquier incumplimiento"
    ]
    
    for i, clause in enumerate(problematic_clauses_normal, 1):
        print(f"  {i}. {clause}")
    
    # Comparación de cláusulas similares
    print("\n🔄 CLÁUSULAS SIMILARES EN AMBOS CONTRATOS:")
    print("-" * 45)
    
    similar_clauses = [
        {
            'type': 'Aumento de renta',
            'contract1': '10% o inflación (lo mayor)',
            'contract2': '10% o inflación (lo mayor)',
            'ml_eval1': 'Válida',
            'ml_eval2': 'Válida',
            'comment': 'ML fue consistente'
        },
        {
            'type': 'Penalidad rescisión',
            'contract1': '1 mes de renta',
            'contract2': '1 mes de renta',
            'ml_eval1': 'Abusiva',
            'ml_eval2': 'Válida',
            'comment': 'ML inconsistente'
        },
        {
            'type': 'Fiador solidario',
            'contract1': 'Presente',
            'contract2': 'Presente',
            'ml_eval1': 'Válida',
            'ml_eval2': 'Abusiva',
            'comment': 'ML inconsistente'
        }
    ]
    
    for clause in similar_clauses:
        print(f"\n📋 {clause['type']}:")
        print(f"  Contrato 1: {clause['contract1']} → {clause['ml_eval1']}")
        print(f"  Contrato 2: {clause['contract2']} → {clause['ml_eval2']}")
        print(f"  Observación: {clause['comment']}")
    
    # Posibles explicaciones
    print("\n🤔 POSIBLES EXPLICACIONES:")
    print("-" * 30)
    
    explanations = [
        "1. El modelo ML fue entrenado con datos específicos que pueden no representar completamente la realidad legal dominicana",
        "2. Las diferencias en redacción y estructura pueden afectar las predicciones del modelo",
        "3. El contrato 'normal' puede tener elementos legalmente problemáticos que el usuario no percibió inicialmente",
        "4. La percepción de 'normalidad' puede estar influida por prácticas comunes pero no necesariamente legales",
        "5. El modelo puede necesitar más datos de entrenamiento específicos del contexto dominicano"
    ]
    
    for explanation in explanations:
        print(f"  {explanation}")
    
    # Recomendaciones para mejorar el sistema
    print("\n💡 RECOMENDACIONES PARA MEJORAR EL SISTEMA:")
    print("-" * 50)
    
    recommendations = [
        "1. Recopilar más datos de contratos dominicanos con etiquetas verificadas por abogados",
        "2. Incluir más artículos del Código Civil en la base RAG",
        "3. Calibrar el modelo con casos específicos de la jurisprudencia dominicana",
        "4. Desarrollar métricas de confianza basadas en el consenso RAG + ML",
        "5. Implementar validación cruzada con expertos legales locales"
    ]
    
    for recommendation in recommendations:
        print(f"  {recommendation}")
    
    # Valor del sistema RAG
    print("\n✅ VALOR AGREGADO DEL SISTEMA RAG:")
    print("-" * 40)
    
    rag_benefits = [
        "• Proporciona contexto legal específico del Código Civil Dominicano",
        "• Referencia artículos relevantes para fundamentar decisiones",
        "• Permite búsqueda semántica de normativa legal",
        "• Facilita la explicabilidad de las decisiones del sistema",
        "• Reduce la dependencia de conocimiento implícito del modelo"
    ]
    
    for benefit in rag_benefits:
        print(f"  {benefit}")
    
    # Conclusiones finales
    print("\n🎯 CONCLUSIONES FINALES:")
    print("-" * 25)
    
    print("✅ ÉXITOS:")
    print("  • El sistema RAG + ML funciona técnicamente")
    print("  • Proporciona referencias legales específicas")
    print("  • Detecta patrones problemáticos en contratos")
    print("  • Procesa contratos complejos en tiempo razonable")
    
    print("\n⚠️ AREAS DE MEJORA:")
    print("  • Calibración del modelo con más datos locales")
    print("  • Consistencia en evaluación de cláusulas similares")
    print("  • Validación con expertos legales dominicanos")
    print("  • Incorporación de más contexto legal en RAG")
    
    print("\n🚀 IMPACTO:")
    print("  • El sistema puede ayudar a identificar cláusulas problemáticas")
    print("  • Proporciona una segunda opinión basada en IA")
    print("  • Facilita el acceso a análisis legal preliminar")
    print("  • Mejora la transparencia del proceso de evaluación")
    
    print(f"\n{'='*65}")
    print("🎉 ANÁLISIS COMPARATIVO COMPLETADO")
    print(f"{'='*65}")


if __name__ == "__main__":
    print_comparative_summary()