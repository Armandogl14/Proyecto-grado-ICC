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

    const response = await fetch(`${BACKEND_URL}/api/contracts/${params.id}/`, {
      method: 'GET',
      headers,
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    })
  } catch (error) {
    console.error('Contract proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch contract from backend' },
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

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const url = new URL(request.url)
    const pathname = url.pathname
    
    // Determinar el endpoint basado en la URL
    let backendEndpoint = `${BACKEND_URL}/api/contracts/${params.id}/`
    
    if (pathname.includes('/analyze')) {
      backendEndpoint = `${BACKEND_URL}/api/contracts/${params.id}/analyze/`
    } else if (pathname.includes('/export_report')) {
      backendEndpoint = `${BACKEND_URL}/api/contracts/${params.id}/export_report/`
    }
    
    const body = await request.json()
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

    const response = await fetch(backendEndpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    })
  } catch (error) {
    console.error('Contract action proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to perform action on backend' },
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

export async function DELETE(
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

    const response = await fetch(`${BACKEND_URL}/api/contracts/${params.id}/`, {
      method: 'DELETE',
      headers,
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    return new NextResponse(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    })
  } catch (error) {
    console.error('Contract delete proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to delete contract from backend' },
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
