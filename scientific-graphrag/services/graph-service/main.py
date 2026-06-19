"""
Graph Service - Phase 5

Handles Neo4j knowledge graph operations
Creates and manages nodes and relationships
"""

from typing import List, Dict, Any, Optional
import logging
import uuid

from shared.utils.logger import setup_logging
from shared.schemas.models import Entity, Relationship, EntityType
from shared.config.settings import settings

logger = setup_logging(__name__)


class Neo4jGraphDB:
    """Neo4j Knowledge Graph Integration"""
    
    def __init__(self, uri: str = settings.NEO4J_URI, user: str = settings.NEO4J_USER, password: str = settings.NEO4J_PASSWORD):
        """Initialize Neo4j driver"""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.init_driver()
    
    def init_driver(self):
        """Initialize Neo4j driver"""
        try:
            from neo4j import GraphDatabase
            logger.info(f"Connecting to Neo4j at {self.uri}")
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("Neo4j driver initialized")
        except Exception as e:
            logger.error(f"Error initializing Neo4j driver: {str(e)}")
            raise
    
    def close(self):
        """Close driver connection"""
        if self.driver:
            self.driver.close()
    
    def create_entity(self, entity: Entity) -> bool:
        """Create an entity node in Neo4j"""
        try:
            with self.driver.session() as session:
                query = f"""
                CREATE (e:{entity.entity_type.value.upper()} {{
                    entity_id: $entity_id,
                    name: $name,
                    properties: $properties
                }})
                RETURN e
                """
                
                result = session.run(
                    query,
                    entity_id=entity.entity_id,
                    name=entity.name,
                    properties=entity.properties
                )
                
                logger.info(f"Created entity: {entity.name} ({entity.entity_type})")
                return True
        except Exception as e:
            logger.error(f"Error creating entity: {str(e)}")
            raise
    
    def create_relationship(self, relationship: Relationship) -> bool:
        """Create a relationship between entities"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (source {entity_id: $source_id})
                MATCH (target {entity_id: $target_id})
                CREATE (source)-[r:RELATED {
                    relationship_id: $relationship_id,
                    relationship_type: $relationship_type,
                    confidence: $confidence,
                    properties: $properties
                }]->(target)
                RETURN r
                """
                
                result = session.run(
                    query,
                    source_id=relationship.source_entity_id,
                    target_id=relationship.target_entity_id,
                    relationship_id=relationship.relationship_id,
                    relationship_type=relationship.relationship_type,
                    confidence=relationship.confidence,
                    properties=relationship.properties
                )
                
                logger.info(f"Created relationship: {relationship.relationship_type}")
                return True
        except Exception as e:
            logger.error(f"Error creating relationship: {str(e)}")
            raise
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (e {entity_id: $entity_id})
                RETURN e
                """
                
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                if record:
                    return dict(record["e"])
                return None
        except Exception as e:
            logger.error(f"Error getting entity: {str(e)}")
            raise
    
    def query_graph(self, cypher_query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query"""
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query, parameters or {})
                records = result.data()
                logger.info(f"Query executed, returned {len(records)} records")
                return records
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise


class GraphService:
    """High-level graph service"""
    
    # Define node types and relationships
    NODE_TYPES = {
        EntityType.CONCEPT: "Concept",
        EntityType.CHEMICAL: "Chemical",
        EntityType.DISEASE: "Disease",
        EntityType.EXPERIMENT: "Experiment",
        EntityType.REFERENCE_RANGE: "ReferenceRange",
        EntityType.AUTHOR: "Author",
        EntityType.PROPERTY: "Property"
    }
    
    RELATIONSHIPS = {
        "CONCEPT_RELATED": ("Concept", "Concept", "RELATED_TO"),
        "CHEMICAL_CAUSES": ("Chemical", "Disease", "CAUSES"),
        "PROPERTY_MEASURED": ("Property", "Experiment", "MEASURED_BY"),
        "PAPER_SUPPORTS": ("Paper", "Concept", "SUPPORTS"),
        "RANGE_APPLIES": ("ReferenceRange", "Property", "APPLIES_TO")
    }
    
    def __init__(self):
        """Initialize graph service"""
        self.graph_db = Neo4jGraphDB()
    
    def add_concept(self, name: str, properties: Dict[str, Any] = None) -> Entity:
        """Add a concept to the graph"""
        entity = Entity(
            entity_id=str(uuid.uuid4()),
            name=name,
            entity_type=EntityType.CONCEPT,
            properties=properties or {},
            document_ids=[]
        )
        self.graph_db.create_entity(entity)
        return entity
    
    def add_chemical(self, name: str, properties: Dict[str, Any] = None) -> Entity:
        """Add a chemical to the graph"""
        entity = Entity(
            entity_id=str(uuid.uuid4()),
            name=name,
            entity_type=EntityType.CHEMICAL,
            properties=properties or {},
            document_ids=[]
        )
        self.graph_db.create_entity(entity)
        return entity
    
    def add_disease(self, name: str, properties: Dict[str, Any] = None) -> Entity:
        """Add a disease to the graph"""
        entity = Entity(
            entity_id=str(uuid.uuid4()),
            name=name,
            entity_type=EntityType.DISEASE,
            properties=properties or {},
            document_ids=[]
        )
        self.graph_db.create_entity(entity)
        return entity
    
    def add_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str,
        confidence: float = 1.0,
        properties: Dict[str, Any] = None
    ) -> Relationship:
        """Add a relationship"""
        relationship = Relationship(
            relationship_id=str(uuid.uuid4()),
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            properties=properties or {},
            confidence=confidence
        )
        self.graph_db.create_relationship(relationship)
        return relationship
    
    def search_entities(self, query: str) -> List[Entity]:
        """Search for entities by name"""
        try:
            cypher_query = """
            MATCH (e)
            WHERE e.name CONTAINS $query
            RETURN e
            LIMIT 10
            """
            
            results = self.graph_db.query_graph(cypher_query, {"query": query})
            entities = []
            for result in results:
                node = result["e"]
                entity = Entity(
                    entity_id=node.get("entity_id"),
                    name=node.get("name"),
                    entity_type=EntityType.CONCEPT,
                    properties=dict(node),
                    document_ids=[]
                )
                entities.append(entity)
            
            return entities
        except Exception as e:
            logger.error(f"Error searching entities: {str(e)}")
            return []


# FastAPI app for graph service
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Graph Service", version="1.0.0")
graph_service = GraphService()


class AddEntityRequest(BaseModel):
    name: str
    entity_type: str
    properties: Dict[str, Any] = {}


class AddRelationshipRequest(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float = 1.0


@app.post("/entities")
async def add_entity(request: AddEntityRequest):
    """Add an entity"""
    try:
        if request.entity_type == "concept":
            entity = graph_service.add_concept(request.name, request.properties)
        elif request.entity_type == "chemical":
            entity = graph_service.add_chemical(request.name, request.properties)
        elif request.entity_type == "disease":
            entity = graph_service.add_disease(request.name, request.properties)
        else:
            return JSONResponse(status_code=400, content={"error": "Unknown entity type"})
        
        return {
            "status": "success",
            "entity_id": entity.entity_id,
            "name": entity.name
        }
    except Exception as e:
        logger.error(f"Error adding entity: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/relationships")
async def add_relationship(request: AddRelationshipRequest):
    """Add a relationship"""
    try:
        relationship = graph_service.add_relationship(
            request.source_entity_id,
            request.target_entity_id,
            request.relationship_type,
            request.confidence
        )
        
        return {
            "status": "success",
            "relationship_id": relationship.relationship_id,
            "type": relationship.relationship_type
        }
    except Exception as e:
        logger.error(f"Error adding relationship: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/search")
async def search_entities(query: str):
    """Search for entities"""
    try:
        entities = graph_service.search_entities(query)
        
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "entity_id": e.entity_id,
                    "name": e.name,
                    "type": e.entity_type
                }
                for e in entities
            ]
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "graph-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
