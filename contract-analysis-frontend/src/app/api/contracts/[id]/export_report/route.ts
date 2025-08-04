import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = 'http://172.245.214.69:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const authHeader = request.headers.get('authorization')
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    
    if (authHeader) {
      headers['Authorization'] = authHeader
    } else {
      // Usar Basic Auth por defecto para desarrollo
      const basicAuth = btoa('admin:admin123')
      headers['Authorization'] = `Basic ${basicAuth}`
    }

    const response = await fetch(`${BACKEND_URL}/api/contracts/${params.id}/export_report/`, {
      method: 'GET',
      headers,
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    // Para archivos blob, devolver directamente la respuesta
    const blob = await response.blob()
    
    return new NextResponse(blob, {
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/octet-stream',
        'Content-Disposition': response.headers.get('Content-Disposition') || 'attachment',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    })
  } catch (error) {
    console.error('Export report proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to export report from backend' },
      { 
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
