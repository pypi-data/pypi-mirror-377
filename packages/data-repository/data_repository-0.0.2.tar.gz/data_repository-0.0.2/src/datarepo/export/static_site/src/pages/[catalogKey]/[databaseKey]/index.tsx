import { Flex, Separator, Text } from '@radix-ui/themes'
import { generatePath, Outlet, useNavigate, useParams, useRouteLoaderData } from 'react-router-dom'

import { ExportedCatalog, ExportedDatabase } from '../../../lib/types'
import Sidebar from '../../../components/Sidebar'

export default function DatabaseKeyPage () {
  const catalog = useRouteLoaderData('catalogKey') as ExportedCatalog
  const database = useRouteLoaderData('databaseKey') as ExportedDatabase | null

  const { tableKey } = useParams()
  const navigate = useNavigate()

  if (!database) {
    return (
      <Flex 
        justify='center' 
        flexGrow='1' 
        p='5'
        className='responsive-container'
      >
        <Text color='gray'>No database selected.</Text>
      </Flex>
    )
  }

  return (
    <Flex 
      flexGrow='1' 
      flexBasis='0%'
      overflow='hidden'
    >
      {/* Desktop Sidebar - Completely hidden on mobile */}
      <Sidebar
        eyebrow={database.name}
        heading='Tables'
        items={database.tables.map((table) => ({
          label: table.name,
          value: table.name
        }))}
        value={tableKey}
        onValueChange={(tableKey) => {
          navigate(generatePath(
            '/:catalogKey/:databaseKey/:tableKey',
            {
              catalogKey: catalog.name,
              databaseKey: database.name,
              tableKey: encodeURIComponent(tableKey)
            }
          ))
        }}
      />

      <Separator 
        orientation='vertical'
        size='4' 
        className='desktop-only'
      />

      {/* Content takes full width on mobile */}
      <Flex 
        flexGrow='1' 
        flexBasis='0%' 
        overflow='hidden'
      >
        <Outlet />
      </Flex>
    </Flex>
  )
}
