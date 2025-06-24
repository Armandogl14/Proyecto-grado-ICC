# 📚 API Documentation - Contract Analysis System

## 🔗 Base URL
```
http://localhost:8000/api/
```

## 🔐 Authentication
La API requiere autenticación. Opciones disponibles:
- **Session Authentication** (para desarrollo)
- **Token Authentication** (recomendado para producción)

### Obtener Token
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

## 📋 Endpoints Principales

### 1. **Contratos** (`/contracts/`)

#### Listar Contratos
```bash
GET /api/contracts/
Authorization: Token your_token_here
```

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/contracts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Contrato de Alquiler - Local Comercial",
      "contract_type": "ALC",
      "contract_type_name": "Contrato de Alquiler",
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "analyzed_at": "2024-01-15T10:35:00Z",
      "total_clauses": 8,
      "abusive_clauses_count": 2,
      "risk_score": 0.75,
      "risk_level": "Alto",
      "uploaded_by_username": "usuario1"
    }
  ]
}
```

#### Crear Contrato
```bash
POST /api/contracts/
Authorization: Token your_token_here
Content-Type: application/json

{
  "title": "Contrato de Venta de Vehículo",
  "contract_type": 1,
  "original_text": "CONTRATO DE VENTA DE VEHÍCULO...",
  "file_upload": null
}
```

#### Obtener Detalle del Contrato
```bash
GET /api/contracts/{id}/
Authorization: Token your_token_here
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Contrato de Alquiler",
  "contract_type": {
    "id": 1,
    "name": "Contrato de Alquiler",
    "code": "ALC"
  },
  "original_text": "CONTRATO DE ALQUILER...",
  "status": "completed",
  "risk_score": 0.75,
  "risk_level": "Alto",
  "clauses": [
    {
      "id": "clause-uuid",
      "text": "El inquilino debe...",
      "clause_number": "PRIMERO",
      "is_abusive": true,
      "confidence_score": 0.85,
      "entities": [
        {
          "text": "El inquilino",
          "label": "PARTES_CONTRATO",
          "start_char": 0,
          "end_char": 12
        }
      ]
    }
  ],
  "analysis_result": {
    "executive_summary": "El contrato presenta riesgo alto...",
    "recommendations": "Se recomienda revisar las cláusulas...",
    "processing_time": 2.5
  }
}
```

#### Analizar Contrato
```bash
POST /api/contracts/{id}/analyze/
Authorization: Token your_token_here
Content-Type: application/json

{
  "force_reanalysis": false
}
```

**Response:**
```json
{
  "message": "Análisis iniciado",
  "contract_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": "celery-task-uuid",
  "status": "analyzing"
}
```

#### Análisis Masivo
```bash
POST /api/contracts/bulk_analyze/
Authorization: Token your_token_here
Content-Type: application/json

{
  "contract_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "456e7890-e89b-12d3-a456-426614174111"
  ],
  "force_reanalysis": false
}
```

#### Estadísticas del Dashboard
```bash
GET /api/contracts/dashboard_stats/
Authorization: Token your_token_here
```

**Response:**
```json
{
  "total_contracts": 25,
  "pending_analysis": 3,
  "analyzing": 1,
  "completed": 21,
  "high_risk": 5,
  "medium_risk": 8,
  "low_risk": 8,
  "recent_contracts": [...]
}
```

#### Exportar Reporte
```bash
GET /api/contracts/{id}/export_report/
Authorization: Token your_token_here
```

### 2. **Tipos de Contratos** (`/contract-types/`)

```bash
GET /api/contract-types/
Authorization: Token your_token_here
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Contrato de Alquiler",
    "code": "ALC",
    "description": "Contratos de arrendamiento de locales y viviendas"
  },
  {
    "id": 2,
    "name": "Venta de Vehículo",
    "code": "VM",
    "description": "Contratos de compraventa de vehículos"
  }
]
```

### 3. **Cláusulas** (`/clauses/`)

#### Listar Cláusulas
```bash
GET /api/clauses/
Authorization: Token your_token_here

# Filtros disponibles:
GET /api/clauses/?is_abusive=true
GET /api/clauses/?clause_type=payment
```

#### Patrones de Cláusulas Abusivas
```bash
GET /api/clauses/abusive_patterns/
Authorization: Token your_token_here
```

**Response:**
```json
{
  "payment": {
    "count": 5,
    "examples": [
      {
        "text": "El inquilino debe pagar impuestos que corresponden al propietario...",
        "confidence": 0.92
      }
    ]
  },
  "termination": {
    "count": 3,
    "examples": [...]
  }
}
```

## 🎨 **Estructura para Frontend React**

### Componentes Recomendados

```typescript
// Types
interface Contract {
  id: string;
  title: string;
  contract_type: string;
  status: 'pending' | 'analyzing' | 'completed' | 'error';
  risk_score: number;
  risk_level: string;
  created_at: string;
  analyzed_at?: string;
  total_clauses: number;
  abusive_clauses_count: number;
}

interface Clause {
  id: string;
  text: string;
  clause_number: string;
  is_abusive: boolean;
  confidence_score: number;
  entities: Entity[];
}

interface Entity {
  text: string;
  label: string;
  start_char: number;
  end_char: number;
  confidence: number;
}
```

### Services (API Calls)

```typescript
// contractService.ts
class ContractService {
  private baseURL = 'http://localhost:8000/api';
  
  async getContracts(page = 1): Promise<ContractList> {
    const response = await fetch(`${this.baseURL}/contracts/?page=${page}`, {
      headers: { 'Authorization': `Token ${getToken()}` }
    });
    return response.json();
  }
  
  async createContract(contractData: CreateContractData): Promise<Contract> {
    const response = await fetch(`${this.baseURL}/contracts/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(contractData)
    });
    return response.json();
  }
  
  async analyzeContract(contractId: string): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseURL}/contracts/${contractId}/analyze/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ force_reanalysis: false })
    });
    return response.json();
  }
  
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await fetch(`${this.baseURL}/contracts/dashboard_stats/`, {
      headers: { 'Authorization': `Token ${getToken()}` }
    });
    return response.json();
  }
}
```

### Estructura de Páginas Recomendada

```
src/
├── components/
│   ├── ContractCard.tsx
│   ├── ClauseHighlighter.tsx
│   ├── RiskIndicator.tsx
│   ├── AnalysisProgress.tsx
│   └── EntityTag.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── ContractList.tsx
│   ├── ContractDetail.tsx
│   ├── ContractUpload.tsx
│   └── AnalysisReport.tsx
├── services/
│   ├── contractService.ts
│   ├── authService.ts
│   └── apiClient.ts
├── hooks/
│   ├── useContracts.ts
│   ├── useAnalysis.ts
│   └── useWebSocket.ts (para updates en tiempo real)
└── types/
    └── contract.types.ts
```

## 🚀 **Estados de la Aplicación**

### Flujo de Análisis
1. **Upload** → Usuario sube contrato
2. **Pending** → Contrato en cola para análisis
3. **Analyzing** → Procesamiento en curso (mostrar progreso)
4. **Completed** → Análisis completado (mostrar resultados)
5. **Error** → Error en procesamiento (mostrar mensaje)

### WebSocket Updates (Opcional)
Para updates en tiempo real del estado de análisis:

```typescript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/contracts/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'analysis_complete') {
    // Update contract status in React state
    updateContractStatus(data.contract_id, 'completed');
  }
};
```

## ⚠️ **Códigos de Error Comunes**

- **401**: No autenticado
- **403**: Sin permisos para este recurso
- **404**: Contrato no encontrado
- **400**: Datos inválidos en la petición
- **500**: Error interno del servidor

## 🔄 **Polling para Estado de Análisis**

Mientras un contrato está en estado "analyzing", el frontend puede hacer polling:

```typescript
const pollAnalysisStatus = async (contractId: string) => {
  const interval = setInterval(async () => {
    const contract = await contractService.getContract(contractId);
    
    if (contract.status === 'completed' || contract.status === 'error') {
      clearInterval(interval);
      // Update UI with final status
    }
  }, 2000); // Poll every 2 seconds
};
``` 