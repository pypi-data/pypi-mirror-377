#!/usr/bin/env python3
"""
Comprehensive demo script showing both single and multi-endpoint usage.
This can be easily converted to a Jupyter notebook.
"""

import asyncio
import json
from pathlib import Path
from boltz2_client import (
    Boltz2Client,
    Boltz2SyncClient,
    MultiEndpointClient,
    LoadBalanceStrategy,
    EndpointConfig,
    VirtualScreening,
    CompoundLibrary,
    AlignmentFileRecord
)

# Test sequences
UBIQUITIN = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"
LYSOZYME = "KVFERCELARTLKRLGMDGYRGISLANWMCLAKWESGYNTRATNYNAGDRSTDYGIFQINSRYWCNDGKTPGAVNACHLSCSALLQDNIADAVACAKRVVRDPQGIRAWVAWRNRCQNRDVRQYVQGCGV"
CDK2 = "MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNHPNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCHSHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKYYSTAVDIWSLGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPSFPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL"

# Ligands
IBUPROFEN = "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
ASPIRIN = "CC(=O)OC1=CC=CC=C1C(=O)O"


async def demo_single_endpoint():
    """Demonstrate single-endpoint usage."""
    print("\n" + "="*60)
    print("1️⃣  SINGLE-ENDPOINT DEMONSTRATIONS")
    print("="*60)
    
    client = Boltz2Client(base_url="http://localhost:8000")
    
    try:
        # 1. Basic protein prediction
        print("\n📊 Basic Protein Structure Prediction")
        print("-" * 40)
        result = await client.predict_protein_structure(
            sequence=UBIQUITIN,
            sampling_steps=10,
            recycling_steps=1
        )
        print(f"✅ Ubiquitin structure predicted")
        print(f"   Confidence: {result.confidence_scores[0]:.3f}")
        
        # 2. Protein-ligand with affinity
        print("\n💊 Protein-Ligand Complex with Affinity")
        print("-" * 40)
        ligand_result = await client.predict_protein_ligand_complex(
            protein_sequence=CDK2[:100],  # Use fragment for speed
            ligand_smiles=IBUPROFEN,
            predict_affinity=True,
            sampling_steps=10,
            recycling_steps=1,
            sampling_steps_affinity=50
        )
        print(f"✅ CDK2-Ibuprofen complex predicted")
        print(f"   Structure confidence: {ligand_result.confidence_scores[0]:.3f}")
        if ligand_result.affinities and "LIG" in ligand_result.affinities:
            affinity = ligand_result.affinities["LIG"]
            pic50 = affinity.affinity_pic50[0]
            print(f"   pIC50: {pic50:.2f}")
            print(f"   IC50: {10**(-pic50) * 1e9:.1f} nM")
        
        # 3. MSA-guided prediction
        print("\n🧬 MSA-Guided Prediction")
        print("-" * 40)
        msa_content = f">seq1\n{UBIQUITIN}\n>seq2\n{UBIQUITIN}"
        msa_record = AlignmentFileRecord(alignment=msa_content, format="a3m")
        
        msa_result = await client.predict_protein_structure(
            sequence=UBIQUITIN,
            msa={"uniref90": {"a3m": msa_record}},
            sampling_steps=10,
            recycling_steps=1
        )
        print(f"✅ MSA-guided structure predicted")
        print(f"   Confidence: {msa_result.confidence_scores[0]:.3f}")
        
    finally:
        await client.close()


async def demo_multi_endpoint():
    """Demonstrate multi-endpoint usage."""
    print("\n" + "="*60)
    print("2️⃣  MULTI-ENDPOINT DEMONSTRATIONS")
    print("="*60)
    
    # Setup multi-endpoint client
    endpoints = [
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003"
    ]
    
    multi_client = MultiEndpointClient(
        endpoints=endpoints,
        strategy=LoadBalanceStrategy.LEAST_LOADED,
        health_check_interval=30.0
    )
    
    try:
        # Check health
        print("\n🏥 Endpoint Health Check")
        print("-" * 40)
        await multi_client.health_check()
        await multi_client.print_status()
        
        # Parallel predictions
        print("\n🚀 Parallel Predictions")
        print("-" * 40)
        sequences = [
            ("Ubiquitin", UBIQUITIN),
            ("Lysozyme fragment", LYSOZYME[:80]),
            ("CDK2 fragment", CDK2[:100]),
            ("Test sequence", "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG")
        ]
        
        tasks = []
        for name, seq in sequences:
            task = multi_client.predict_protein_structure(
                sequence=seq,
                sampling_steps=10,
                recycling_steps=1
            )
            tasks.append((name, task))
        
        print("Running 4 predictions in parallel...")
        for name, task in tasks:
            try:
                result = await task
                print(f"✅ {name}: Confidence = {result.confidence_scores[0]:.3f}")
            except Exception as e:
                print(f"❌ {name}: Failed - {str(e)}")
        
        # Show final statistics
        print("\n📊 Final Endpoint Statistics:")
        await multi_client.print_status()
        
        # Virtual screening demo
        print("\n🔬 Virtual Screening")
        print("-" * 40)
        compounds = [
            {"name": "Aspirin", "smiles": ASPIRIN},
            {"name": "Ibuprofen", "smiles": IBUPROFEN},
            {"name": "Caffeine", "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"},
        ]
        
        library = CompoundLibrary.from_list(compounds)
        vs = VirtualScreening(client=multi_client)
        
        screening_result = await vs.screen(
            target_sequence="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
            compound_library=library,
            target_name="Demo Target",
            predict_affinity=True,
            batch_size=2,
            recycling_steps=1,
            sampling_steps=10
        )
        
        print(f"✅ Screened {len(compounds)} compounds")
        print("\nTop Hits:")
        for i, hit in enumerate(screening_result.get_top_hits(n=3), 1):
            print(f"{i}. {hit['compound_name']}")
        
    finally:
        await multi_client.close()


def demo_cli_commands():
    """Show CLI command examples."""
    print("\n" + "="*60)
    print("3️⃣  CLI COMMAND EXAMPLES")
    print("="*60)
    
    print("\n📋 Single-Endpoint CLI Commands:")
    print("-" * 40)
    
    cli_commands = [
        # Single endpoint
        "# Health check",
        "python -m boltz2_client --base-url http://localhost:8000 health",
        "",
        "# Protein structure prediction",
        'python -m boltz2_client --base-url http://localhost:8000 protein "MKTVRQERLKSIVRILERSKEPVSGAQ..." --sampling-steps 10',
        "",
        "# Protein-ligand with affinity",
        'python -m boltz2_client --base-url http://localhost:8000 ligand "PROTEIN_SEQ" --smiles "CC(=O)OC1=CC=CC=C1C(=O)O" --predict-affinity',
        "",
        "# MSA-guided prediction",
        'python -m boltz2_client --base-url http://localhost:8000 protein "SEQUENCE" --msa-file alignment.a3m a3m',
    ]
    
    for cmd in cli_commands:
        print(cmd)
    
    print("\n📋 Multi-Endpoint CLI Commands:")
    print("-" * 40)
    
    multi_cli_commands = [
        "# Multi-endpoint health check",
        'python -m boltz2_client --base-url "http://localhost:8000,http://localhost:8001" --multi-endpoint health',
        "",
        "# Multi-endpoint protein prediction",
        'python -m boltz2_client --base-url "http://localhost:8000,http://localhost:8001" --multi-endpoint --load-balance-strategy least_loaded protein "SEQUENCE"',
        "",
        "# Virtual screening with multi-endpoint",
        'python -m boltz2_client --base-url "http://localhost:8000,http://localhost:8001,http://localhost:8002" --multi-endpoint screen "TARGET_SEQ" compounds.csv',
    ]
    
    for cmd in multi_cli_commands:
        print(cmd)


async def main():
    """Run all demonstrations."""
    print("🧬 BOLTZ-2 PYTHON CLIENT - COMPREHENSIVE DEMONSTRATION")
    print("=" * 60)
    print("This demo shows single and multi-endpoint usage patterns")
    print("for both Python API and CLI approaches.")
    
    # Run demos
    await demo_single_endpoint()
    await demo_multi_endpoint()
    demo_cli_commands()
    
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE!")
    print("="*60)
    print("\nKey Takeaways:")
    print("- Single-endpoint: Simple, straightforward usage")
    print("- Multi-endpoint: Better throughput, fault tolerance")
    print("- CLI: Available for both single and multi-endpoint modes")
    print("- Virtual screening: Leverages multi-endpoint for speed")
    print("\nFor more information, see the documentation.")


if __name__ == "__main__":
    asyncio.run(main())
